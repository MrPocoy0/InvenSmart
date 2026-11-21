from flask import Blueprint, flash, render_template, request

from app.services.gemini_service import GeminiServiceError, ask_gemini
from app.services.inventory_context_service import build_inventory_context

ai_bp = Blueprint("ai", __name__, url_prefix="/asistente")
MAX_QUESTION_LENGTH = 1000


@ai_bp.route("/", methods=["GET", "POST"])
def assistant():
    answer = None
    question = ""
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if not question:
            flash("Escribe una pregunta para el asistente.", "error")
        elif len(question) > MAX_QUESTION_LENGTH:
            flash("La pregunta no puede superar 1000 caracteres.", "error")
        else:
            try:
                answer = ask_gemini(question, build_inventory_context())
            except GeminiServiceError as exc:
                flash(str(exc), "error")
    return render_template("ai_assistant.html", answer=answer, question=question)
