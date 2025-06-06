"""
Admin routes for user management and system administration
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.analysis import AnalysisTask, DomainResult, Report
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    """List all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.contains(search),
                    User.email.contains(search)
                )
            )
        
        users = query.order_by(User.created_at.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to list users: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@require_admin
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['user', 'admin']:
            return jsonify({'message': 'Invalid role. Must be "user" or "admin"'}), 400
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update user role: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@require_admin
def update_user_status(user_id):
    """Update user active status (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'message': 'is_active field is required'}), 400
        
        user.is_active = bool(is_active)
        db.session.commit()
        
        return jsonify({
            'message': 'User status updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update user status: {str(e)}'}), 500

@admin_bp.route('/stats', methods=['GET'])
@require_admin
def get_system_stats():
    """Get system statistics (admin only)"""
    try:
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role='admin').count()
        
        # Analysis statistics
        total_tasks = AnalysisTask.query.count()
        completed_tasks = AnalysisTask.query.filter_by(status='completed').count()
        failed_tasks = AnalysisTask.query.filter_by(status='failed').count()
        running_tasks = AnalysisTask.query.filter_by(status='running').count()
        
        # Domain statistics
        total_domains = DomainResult.query.count()
        recommended_domains = DomainResult.query.filter_by(recommended=True).count()
        
        # Report statistics
        total_reports = Report.query.count()
        public_reports = Report.query.filter_by(is_public=True).count()
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'admins': admin_users,
                'inactive': total_users - active_users
            },
            'analysis': {
                'total_tasks': total_tasks,
                'completed': completed_tasks,
                'failed': failed_tasks,
                'running': running_tasks,
                'pending': total_tasks - completed_tasks - failed_tasks - running_tasks
            },
            'domains': {
                'total': total_domains,
                'recommended': recommended_domains,
                'not_recommended': total_domains - recommended_domains
            },
            'reports': {
                'total': total_reports,
                'public': public_reports,
                'private': total_reports - public_reports
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get system stats: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Delete user and all associated data (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent admin from deleting themselves
        if user_id == current_user_id:
            return jsonify({'message': 'Cannot delete your own account'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Delete user and cascade delete all related data
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete user: {str(e)}'}), 500

@admin_bp.route('/tasks', methods=['GET'])
@require_admin
def list_all_tasks():
    """List all analysis tasks (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = AnalysisTask.query
        
        if status:
            query = query.filter_by(status=status)
        
        tasks = query.order_by(AnalysisTask.created_at.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks.items],
            'total': tasks.total,
            'pages': tasks.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to list tasks: {str(e)}'}), 500

