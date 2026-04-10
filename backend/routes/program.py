from flask import Blueprint, jsonify, request

from services.runner import get_program_by_id, get_programs

program_bp = Blueprint("program", __name__)


@program_bp.get("/programs")
def list_programs():
    return jsonify(get_programs())


@program_bp.get("/program/")
def get_program():
    program_id = request.args.get("id", "").strip()
    if not program_id:
        return jsonify(
            {
                "error": "missing_program_id",
                "message": "请通过查询参数 id 提供项目 ID，例如 /api/program/?id=focus-timer",
            }
        ), 400

    program = get_program_by_id(program_id)
    if not program:
        return jsonify({"error": "not_found", "message": f"Program '{program_id}' not found"}), 404

    return jsonify(program)


@program_bp.get("/program/<program_id>")
def get_program_by_path(program_id: str):
    program = get_program_by_id(program_id)
    if not program:
        return jsonify({"error": "not_found", "message": f"Program '{program_id}' not found"}), 404
    return jsonify(program)
