from flask import Flask, render_template, send_file, abort, url_for
import os
import json
from collections import defaultdict

app = Flask(__name__)
BASE_DIR = 'registered_faces'

def load_all_students():
    students = []
    if not os.path.exists(BASE_DIR):
        return students

    for year in os.listdir(BASE_DIR):
        year_path = os.path.join(BASE_DIR, year)
        if not os.path.isdir(year_path):
            continue
        for branch in os.listdir(year_path):
            branch_path = os.path.join(year_path, branch)
            if not os.path.isdir(branch_path):
                continue
            for section in os.listdir(branch_path):
                section_path = os.path.join(branch_path, section)
                if not os.path.isdir(section_path):
                    continue
                for student_folder in os.listdir(section_path):
                    student_path = os.path.join(section_path, student_folder)
                    info_path = os.path.join(student_path, 'info.json')
                    if os.path.exists(info_path):
                        with open(info_path, 'r') as f:
                            info = json.load(f)

                        # Basic required fields with fallbacks
                        info['folder'] = student_folder
                        info['year'] = year
                        info['branch'] = branch
                        info['section'] = section
                        info['id'] = info.get('id', student_folder)
                        info['name'] = info.get('name', 'Unknown')
                        info['roll'] = info.get('roll', 'N/A')

                        # Attach face image preview
                        faces_dir = os.path.join(student_path, 'faces')
                        if os.path.exists(faces_dir):
                            images = sorted([
                                f for f in os.listdir(faces_dir)
                                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                            ])
                            if images:
                                info['image'] = url_for('serve_face',
                                                        year=year,
                                                        branch=branch,
                                                        section=section,
                                                        student_folder=student_folder,
                                                        filename=images[0])
                        students.append(info)
    return students

def group_by_year_branch_section(students):
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for s in students:
        data[s['year']][s['branch']][s['section']].append(s)
    for year in data:
        for branch in data[year]:
            for section in data[year][branch]:
                try:
                    data[year][branch][section].sort(key=lambda x: int(x['roll']))
                except Exception:
                    data[year][branch][section].sort(key=lambda x: x['roll'])
    return data

@app.route('/')
def index():
    students = load_all_students()
    grouped = group_by_year_branch_section(students)
    return render_template('index.html', years=grouped.keys())

@app.route('/year/<year>')
def branches(year):
    students = load_all_students()
    grouped = group_by_year_branch_section(students)
    if year not in grouped:
        abort(404)
    return render_template('branches.html', year=year, branches=grouped[year].keys())

@app.route('/year/<year>/<branch>')
def sections(year, branch):
    students = load_all_students()
    grouped = group_by_year_branch_section(students)
    if year not in grouped or branch not in grouped[year]:
        abort(404)
    return render_template('sections.html', year=year, branch=branch, sections=grouped[year][branch].keys())

@app.route('/year/<year>/<branch>/<section>')
def student_list(year, branch, section):
    students = load_all_students()
    grouped = group_by_year_branch_section(students)
    try:
        student_group = grouped[year][branch][section]
    except KeyError:
        abort(404)
    return render_template('student.html', students=student_group, year=year, branch=branch, section=section)

@app.route('/student/<year>/<id>')
def student_details(year, id):
    students = load_all_students()
    for s in students:
        if s['year'] == year and str(s['id']) == str(id):
            folder = s.get('folder')
            branch = s.get('branch')
            section = s.get('section')
            best_face = None
            if folder:
                faces_dir = os.path.join(BASE_DIR, year, branch, section, folder, 'faces')
                if os.path.exists(faces_dir):
                    images = sorted([
                        f for f in os.listdir(faces_dir)
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                    ])
                    if images:
                        best_face = images[0]
            return render_template(
                'student_details.html',
                student=s,
                best_face=best_face,
                year=year,
                branch=branch,
                section=section,
                student_folder=folder
            )
    abort(404)

@app.route('/face/<year>/<branch>/<section>/<student_folder>/<filename>')
def serve_face(year, branch, section, student_folder, filename):
    face_path = os.path.join(BASE_DIR, year, branch, section, student_folder, 'faces', filename)
    if not os.path.exists(face_path):
        face_path = os.path.join(BASE_DIR, year, branch, section, student_folder, filename)
    if os.path.exists(face_path):
        return send_file(face_path)
    abort(404)

if __name__ == '__main__':
    app.run(debug=True)
