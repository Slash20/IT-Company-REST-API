from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="IT Company API")

templates = Jinja2Templates(directory="templates")

# Конфигурация базы данных
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

DB_SCHEMA = os.getenv("DB_SCHEMA", "ics")

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/employees")
async def get_employees():
    """Получить всех сотрудников"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT e.id, e.first_name, e.last_name, e.email, e.position, e.salary, d.name as department_name
            FROM {DB_SCHEMA}."Employee" e
            JOIN {DB_SCHEMA}."Department" d ON e.id_department = d.id
            ORDER BY e.id
        """)
        employees = cur.fetchall()
        cur.close()
        conn.close()
        return {"success": True, "data": employees}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/employees")
async def add_employee(
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        position: str = Form(...),
        salary: float = Form(...),
        department_id: int = Form(...)
):
    """Добавить сотрудника"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {DB_SCHEMA}."Employee" (first_name, last_name, email, position, salary, id_department)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (first_name, last_name, email, position, salary, department_id))
        new_id = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "message": "Сотрудник добавлен", "id": new_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.put("/api/employees/{employee_id}")
async def update_employee(
        employee_id: int,
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        position: str = Form(...),
        salary: float = Form(...),
        department_id: int = Form(...)
):
    """Обновить сотрудника"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            UPDATE {DB_SCHEMA}."Employee" 
            SET first_name = %s, last_name = %s, email = %s, position = %s, salary = %s, id_department = %s
            WHERE id = %s
        """, (first_name, last_name, email, position, salary, department_id, employee_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "message": "Сотрудник обновлен"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/employees/{employee_id}")
async def delete_employee(employee_id: int):
    """Удалить сотрудника"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Сначала удаляем связи
        cur.execute(f'DELETE FROM {DB_SCHEMA}."Employee_Project" WHERE "Employee_id" = %s', (employee_id,))
        cur.execute(f'DELETE FROM {DB_SCHEMA}."Employee_Task" WHERE "Employee_id" = %s', (employee_id,))
        cur.execute(f"DELETE FROM {DB_SCHEMA}.\"Employee\" WHERE id = %s", (employee_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "message": "Сотрудник удален"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/projects")
async def get_projects():
    """Получить все проекты"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT id, name, description, status, budget, client, date_start, date_end
            FROM {DB_SCHEMA}."Project"
            ORDER BY id
        """)
        projects = cur.fetchall()
        cur.close()
        conn.close()
        return {"success": True, "data": projects}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/projects")
async def add_project(
        name: str = Form(...),
        description: str = Form(""),
        status: str = Form(...),
        budget: float = Form(...),
        client: str = Form(...),
        date_start: Optional[str] = Form(None),
        date_end: Optional[str] = Form(None)
):
    """Добавить проект"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {DB_SCHEMA}."Project" (name, description, status, budget, client, date_start, date_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (name, description, status, budget, client, date_start, date_end))
        new_id = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "message": "Проект добавлен", "id": new_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.put("/api/projects/{project_id}")
async def update_project(
        project_id: int,
        name: str = Form(...),
        description: str = Form(""),
        status: str = Form(...),
        budget: float = Form(...),
        client: str = Form(...),
        date_start: Optional[str] = Form(None),
        date_end: Optional[str] = Form(None)
):
    """Обновить проект"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            UPDATE {DB_SCHEMA}."Project" 
            SET name = %s, description = %s, status = %s, budget = %s, client = %s, date_start = %s, date_end = %s
            WHERE id = %s
        """, (name, description, status, budget, client, date_start, date_end, project_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "message": "Проект обновлен"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int):
    """Удалить проект"""
    try:
        if project_id <= 0:
            return {"success": False, "error": "ID проекта должен быть больше 0"}

        conn = get_db_connection()
        cur = conn.cursor()
        # Проверяем существование
        cur.execute(f"SELECT id FROM {DB_SCHEMA}.\"Project\" WHERE id = %s", (project_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return {"success": False, "error": f"Проект с ID {project_id} не существует"}

        # Удаляем связанные данные
        cur.execute(f'DELETE FROM {DB_SCHEMA}."Employee_Project" WHERE "Project_id" = %s', (project_id,))
        cur.execute(f'DELETE FROM {DB_SCHEMA}."Project_Technology" WHERE "Project_id" = %s', (project_id,))
        cur.execute(f"DELETE FROM {DB_SCHEMA}.\"Task\" WHERE id_project = %s", (project_id,))
        cur.execute(f"DELETE FROM {DB_SCHEMA}.\"Project\" WHERE id = %s", (project_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "message": f"Проект с ID {project_id} удален"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/departments")
async def get_departments():
    """Получить все департаменты"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT id, name, description, budget FROM {DB_SCHEMA}.\"Department\" ORDER BY id")
        departments = cur.fetchall()
        cur.close()
        conn.close()
        return {"success": True, "data": departments}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    print(f"Запуск API с использованием схемы: {DB_SCHEMA}")
    uvicorn.run(app, host="127.0.0.1", port=8000)