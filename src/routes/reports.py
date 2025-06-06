"""
Reports routes for saving and managing analysis reports
"""
import uuid
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.analysis import AnalysisTask, DomainResult, Report

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/', methods=['GET'])
@jwt_required()
def list_reports():
    """List user's saved reports"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        reports = Report.query.filter_by(user_id=current_user_id)\
                             .order_by(Report.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'reports': [report.to_dict() for report in reports.items],
            'total': reports.total,
            'pages': reports.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to list reports: {str(e)}'}), 500

@reports_bp.route('/', methods=['POST'])
@jwt_required()
def save_report():
    """Save selected domains as a report"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Report name is required'}), 400
        
        task_id = data.get('task_id')
        selected_domain_ids = data.get('selected_domains', [])
        
        # Validate task ownership
        if task_id:
            task = AnalysisTask.query.filter_by(id=task_id, user_id=current_user_id).first()
            if not task:
                return jsonify({'message': 'Task not found'}), 404
        
        # Get selected domains data
        domains_data = []
        if selected_domain_ids:
            domains = DomainResult.query.filter(
                DomainResult.id.in_(selected_domain_ids),
                DomainResult.task_id == task_id
            ).all()
            domains_data = [domain.to_dict() for domain in domains]
        
        # Create report
        report_id = str(uuid.uuid4())
        report = Report(
            id=report_id,
            user_id=current_user_id,
            task_id=task_id,
            name=data['name'],
            description=data.get('description', ''),
            domains_data=json.dumps(domains_data),
            is_public=data.get('is_public', False)
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Report saved successfully',
            'report': report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to save report: {str(e)}'}), 500

@reports_bp.route('/<report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get specific report"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user owns the report or if it's public
        report = Report.query.filter(
            db.and_(
                Report.id == report_id,
                db.or_(
                    Report.user_id == current_user_id,
                    Report.is_public == True
                )
            )
        ).first()
        
        if not report:
            return jsonify({'message': 'Report not found'}), 404
        
        return jsonify(report.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get report: {str(e)}'}), 500

@reports_bp.route('/<report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    """Update report"""
    try:
        current_user_id = get_jwt_identity()
        report = Report.query.filter_by(id=report_id, user_id=current_user_id).first()
        
        if not report:
            return jsonify({'message': 'Report not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            report.name = data['name']
        if 'description' in data:
            report.description = data['description']
        if 'is_public' in data:
            report.is_public = data['is_public']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Report updated successfully',
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update report: {str(e)}'}), 500

@reports_bp.route('/<report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete report"""
    try:
        current_user_id = get_jwt_identity()
        report = Report.query.filter_by(id=report_id, user_id=current_user_id).first()
        
        if not report:
            return jsonify({'message': 'Report not found'}), 404
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Report deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete report: {str(e)}'}), 500

@reports_bp.route('/public', methods=['GET'])
def list_public_reports():
    """List public reports (no authentication required)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        reports = Report.query.filter_by(is_public=True)\
                             .order_by(Report.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'reports': [report.to_dict() for report in reports.items],
            'total': reports.total,
            'pages': reports.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to list public reports: {str(e)}'}), 500

