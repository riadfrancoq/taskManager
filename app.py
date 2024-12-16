import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
import json
import os


Base = declarative_base()
engine = create_engine("sqlite:///tasks.db")
SessionLocal = sessionmaker(bind=engine)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, unique=True)
    description = Column(String)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

def get_tasks(db_session):
    return db_session.query(Task).all()

def add_task(db_session, title, description):
    existing_task = db_session.query(Task).filter(Task.title == title).first()
    if existing_task:
        return None  
    db_task = Task(title=title, description=description)
    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)
    return db_task

def mark_task_completed(db_session, task_id):
    task = db_session.query(Task).filter(Task.id == task_id).first()
    if task:
        task.completed = True
        db_session.commit()
        db_session.refresh(task)
    return task

def delete_task(db_session, task_id):
    task = db_session.query(Task).filter(Task.id == task_id).first()
    if task:
        db_session.delete(task)
        db_session.commit()

def save_tasks_to_json(db_session, filename):
    tasks = get_tasks(db_session)
    tasks_data = [{"id": task.id, "title": task.title, "description": task.description, "completed": task.completed} for task in tasks]
    with open(filename, 'w') as f:
        json.dump(tasks_data, f)

def load_tasks_from_json(db_session, filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            tasks_data = json.load(f)
            for task_data in tasks_data:
                task = Task(title=task_data['title'], description=task_data['description'], completed=task_data['completed'])
                db_session.add(task)
            db_session.commit()

def app():
    st.title("Gestión de Tareas")

    db_session = SessionLocal()

    menu = ["Agregar Tarea", "Listar Tareas", "Marcar Completada", "Eliminar Tarea", "Guardar Tareas", "Cargar Tareas"]
    choice = st.sidebar.selectbox("Selecciona una opción", menu)

    if choice == "Agregar Tarea":
        st.subheader("Nueva Tarea")
        title = st.text_input("Título de la tarea")
        description = st.text_area("Descripción de la tarea")
        if st.button("Agregar"):
            if title and description:
                task = add_task(db_session, title, description)
                if task:
                    st.success(f"Tarea '{title}' agregada exitosamente.")
                else:
                    st.error(f"Ya existe una tarea con el título '{title}'.")
            else:
                st.error("Por favor ingresa el título y la descripción.")

    elif choice == "Listar Tareas":
        st.subheader("Lista de Tareas")
        tasks = get_tasks(db_session)
        for task in tasks:
            st.write(f"**{task.title}** - {task.description} - {'Completada' if task.completed else 'Pendiente'}")

    elif choice == "Marcar Completada":
        st.subheader("Marcar Tarea como Completada")
        tasks = get_tasks(db_session)
        pending_tasks = [task for task in tasks if not task.completed]
        
        if pending_tasks:
            task_titles = [task.title for task in pending_tasks]
            selected_task_title = st.selectbox("Selecciona una tarea", task_titles)
            if st.button("Marcar como completada"):
                selected_task = next(task for task in pending_tasks if task.title == selected_task_title)
                mark_task_completed(db_session, selected_task.id)
                st.success(f"Tarea '{selected_task.title}' marcada como completada.")
        else:
            st.write("No hay tareas pendientes.")

    elif choice == "Eliminar Tarea":
        st.subheader("Eliminar Tarea")
        tasks = get_tasks(db_session)
        if tasks:
            task_titles = [task.title for task in tasks]
            selected_task_title = st.selectbox("Selecciona una tarea a eliminar", task_titles)
            if st.button("Eliminar"):
                selected_task = next(task for task in tasks if task.title == selected_task_title)
                delete_task(db_session, selected_task.id)
                st.success(f"Tarea '{selected_task.title}' eliminada.")
        else:
            st.write("No hay tareas para eliminar.")

    elif choice == "Guardar Tareas":
        st.subheader("Guardar Tareas en Archivo")
        filename = st.text_input("Nombre del archivo", "tasks.json")
        if st.button("Guardar"):
            save_tasks_to_json(db_session, filename)
            st.success(f"Tareas guardadas en '{filename}'.")

    elif choice == "Cargar Tareas":
        st.subheader("Cargar Tareas desde Archivo")
        filename = st.text_input("Nombre del archivo", "tasks.json")
        if st.button("Cargar"):
            load_tasks_from_json(db_session, filename)
            st.success(f"Tareas cargadas desde '{filename}'.")

    db_session.close()

if __name__ == "__main__":
    app()
