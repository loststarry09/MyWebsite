from time import time
from flask import Blueprint, jsonify, request

from services.runner import (
    add_fun_item,
    add_program,
    get_fun_items,
    get_program_by_id,
    get_programs,
)

program_bp = Blueprint("program", __name__)


def _validate_required_string(payload: dict, field: str, max_length: int):
    value = payload.get(field, "")
    if not isinstance(value, str) or not value.strip():
        return None, f"字段 {field} 不能为空"
    value = value.strip()
    if len(value) > max_length:
        return None, f"字段 {field} 长度不能超过 {max_length}"
    return value, None


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


@program_bp.post("/program")
def create_program():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_json", "message": "请求体必须是 JSON 对象"}), 400

    name, error = _validate_required_string(payload, "name", 30)
    if error:
        return jsonify({"error": "validation_error", "message": error}), 400

    description, error = _validate_required_string(payload, "description", 100)
    if error:
        return jsonify({"error": "validation_error", "message": error}), 400

    tech_stack, error = _validate_required_string(payload, "techStack", 100)
    if error:
        return jsonify({"error": "validation_error", "message": error}), 400

    status, error = _validate_required_string(payload, "status", 30)
    if error:
        return jsonify({"error": "validation_error", "message": error}), 400

    api, error = _validate_required_string(payload, "api", 200)
    if error:
        return jsonify({"error": "validation_error", "message": error}), 400

    new_program = {
        "id": f"custom-{int(time() * 1000)}",
        "name": name,
        "summary": description,
        "stack": [item.strip() for item in tech_stack.replace("，", ",").split(",") if item.strip()],
        "status": status,
        "api": api,
        "isCustom": True,
    }
    return jsonify(add_program(new_program)), 201


@program_bp.post("/fun")
def create_fun():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_json", "message": "请求体必须是 JSON 对象"}), 400

    name, error = _validate_required_string(payload, "name", 30)
    if error:
        return jsonify({"error": "validation_error", "message": error}), 400

    description, error = _validate_required_string(payload, "description", 100)
    if error:
        return jsonify({"error": "validation_error", "message": error}), 400

    api, error = _validate_required_string(payload, "api", 200)
    if error:
        return jsonify({"error": "validation_error", "message": error}), 400

    new_fun = {
        "id": f"fun-{int(time() * 1000)}",
        "name": name,
        "description": description,
        "api": api,
    }
    return jsonify(add_fun_item(new_fun)), 201


@program_bp.get("/fun")
def list_fun():
    return jsonify(get_fun_items())

