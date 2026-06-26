from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import Resume, ChatSession, ChatMessage
from extensions import db
from services.chat_service import chunk_resume_data

chat_bp = Blueprint('chat', __name__, url_prefix='/chat', template_folder='../templates')

@chat_bp.route('/api/session', methods=['POST'])
@login_required
def get_or_create_session():
    data = request.json
    resume_id = data.get('resume_id')
    if resume_id == "":
        resume_id = None
        
    resume = None
    if resume_id:
        resume = Resume.query.get(resume_id)
        if not resume or resume.user_id != current_user.id:
            return jsonify({"error": "Resume not found"}), 404
        session = ChatSession.query.filter_by(user_id=current_user.id, resume_id=resume.id).order_by(ChatSession.created_at.desc()).first()
    else:
        session = ChatSession.query.filter_by(user_id=current_user.id, resume_id=None).order_by(ChatSession.created_at.desc()).first()
    
    if not session:
        session = ChatSession(user_id=current_user.id, resume_id=resume.id if resume else None)
        db.session.add(session)
        db.session.commit()
        
        # Initialize RAG chunks in background if resume exists
        if resume:
            try:
                chunk_resume_data(resume)
            except Exception as e:
                print("Error chunking resume:", e)
            
    # Fetch history
    messages = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.created_at.asc()).all()
    history = [{"role": m.role, "content": m.content, "time": m.created_at.strftime("%H:%M")} for m in messages]
    
    return jsonify({
        "session_id": session.id,
        "history": history
    })


@chat_bp.route('/api/message/stream', methods=['POST'])
@login_required
def send_message_stream():
    from flask import Response
    data = request.json
    session_id = data.get('session_id')
    content = data.get('content')
    resume_id = data.get('resume_id')
    if resume_id == "":
        resume_id = None
    
    if not session_id or not content:
        return jsonify({"error": "Missing parameters"}), 400
        
    session = ChatSession.query.get(session_id)
    if not session or session.user_id != current_user.id:
        return jsonify({"error": "Invalid session"}), 403
        
    resume = None
    if resume_id:
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({"error": "Resume not found"}), 404
        
    # Ensure chunks exist before processing message if resume
    if resume:
        try:
            chunk_resume_data(resume)
        except Exception as e:
            print("Error chunking resume in message:", e)
        
    from services.chat_service import process_chat_message_stream
    return Response(process_chat_message_stream(session.id, content, resume), mimetype='text/event-stream')
