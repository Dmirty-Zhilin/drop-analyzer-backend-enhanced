"""
Analysis routes with AI integration and domain selection
"""
import uuid
import asyncio
import json
import statistics
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.analysis import AnalysisTask, DomainResult
from src.services.wayback_analyzer import WaybackAnalyzer
from src.services.ai_analyzer import AIAnalyzer
from src.services.export_service import ExportService
import io
import pandas as pd

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analyze', methods=['POST'])
@jwt_required()
def start_analysis():
    """Start domain analysis task"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('domains'):
            return jsonify({'message': 'Domains list is required'}), 400
        
        # Create analysis task
        task_id = str(uuid.uuid4())
        task = AnalysisTask(
            id=task_id,
            user_id=current_user_id,
            task_name=data.get('task_name', f'Analysis {datetime.now().strftime("%Y-%m-%d %H:%M")}'),
            domains_count=len(data['domains']),
            use_test_data=data.get('use_test_data', False),
            ai_analysis_enabled=data.get('ai_analysis_enabled', True)
        )
        
        db.session.add(task)
        db.session.commit()
        
        # Start analysis in background
        asyncio.create_task(run_analysis_task(task_id, data['domains']))
        
        return jsonify({
            'id': task_id,
            'message': 'Analysis started',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to start analysis: {str(e)}'}), 500

@analysis_bp.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """Get analysis task status"""
    try:
        current_user_id = get_jwt_identity()
        task = AnalysisTask.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'message': 'Task not found'}), 404
        
        return jsonify(task.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get task status: {str(e)}'}), 500

@analysis_bp.route('/tasks', methods=['GET'])
@jwt_required()
def list_tasks():
    """List user's analysis tasks"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        tasks = AnalysisTask.query.filter_by(user_id=current_user_id)\
                                 .order_by(AnalysisTask.created_at.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks.items],
            'total': tasks.total,
            'pages': tasks.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to list tasks: {str(e)}'}), 500

@analysis_bp.route('/results/<task_id>/select', methods=['POST'])
@jwt_required()
def update_domain_selection(task_id):
    """Update domain selection status"""
    try:
        current_user_id = get_jwt_identity()
        task = AnalysisTask.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'message': 'Task not found'}), 404
        
        data = request.get_json()
        domain_selections = data.get('selections', {})  # {domain_id: boolean}
        
        for domain_id, is_selected in domain_selections.items():
            domain_result = DomainResult.query.filter_by(id=domain_id, task_id=task_id).first()
            if domain_result:
                domain_result.is_selected = is_selected
        
        db.session.commit()
        
        return jsonify({'message': 'Selection updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update selection: {str(e)}'}), 500

@analysis_bp.route('/export/<task_id>', methods=['GET'])
@jwt_required()
def export_results(task_id):
    """Export analysis results"""
    try:
        current_user_id = get_jwt_identity()
        task = AnalysisTask.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'message': 'Task not found'}), 404
        
        export_format = request.args.get('format', 'excel')
        selected_only = request.args.get('selected_only', 'false').lower() == 'true'
        
        # Get results
        query = DomainResult.query.filter_by(task_id=task_id)
        if selected_only:
            query = query.filter_by(is_selected=True)
        
        results = query.all()
        
        if not results:
            return jsonify({'message': 'No results found'}), 404
        
        # Export data
        export_service = ExportService()
        
        if export_format == 'excel':
            file_data = export_service.export_to_excel(results, task.task_name)
            filename = f"{task.task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif export_format == 'csv':
            file_data = export_service.export_to_csv(results)
            filename = f"{task.task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            mimetype = 'text/csv'
        elif export_format == 'json':
            file_data = export_service.export_to_json(results)
            filename = f"{task.task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            mimetype = 'application/json'
        else:
            return jsonify({'message': 'Unsupported export format'}), 400
        
        return send_file(
            io.BytesIO(file_data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'message': f'Failed to export results: {str(e)}'}), 500

async def run_analysis_task(task_id, domains):
    """Run analysis task in background"""
    try:
        task = AnalysisTask.query.get(task_id)
        if not task:
            return
        
        task.status = 'running'
        task.started_at = datetime.utcnow()
        db.session.commit()
        
        wayback_analyzer = WaybackAnalyzer()
        ai_analyzer = AIAnalyzer() if task.ai_analysis_enabled else None
        
        total_domains = len(domains)
        
        for i, domain in enumerate(domains):
            try:
                # Update progress
                task.current_domain = domain
                task.progress = int((i / total_domains) * 100)
                db.session.commit()
                
                # Analyze domain with Wayback Machine
                wayback_data = await wayback_analyzer.analyze_domain(domain, task.use_test_data)
                
                # AI analysis if enabled
                ai_data = {}
                if ai_analyzer and wayback_data.get('has_snapshot'):
                    ai_data = await ai_analyzer.analyze_domain_theme(domain)
                
                # Create domain result
                domain_result = DomainResult(
                    task_id=task_id,
                    domain_name=domain,
                    **wayback_data,
                    **ai_data
                )
                
                db.session.add(domain_result)
                db.session.commit()
                
            except Exception as e:
                print(f"Error analyzing domain {domain}: {str(e)}")
                continue
        
        # Complete task
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        task.progress = 100
        task.current_domain = None
        db.session.commit()
        
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        db.session.commit()

