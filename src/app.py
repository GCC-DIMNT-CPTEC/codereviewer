import os
import uuid
from flask import Flask, request, render_template, jsonify, send_file, after_this_request
#from flask_wtf.csrf import CSRFProtect
from fparser.common.readfortran import FortranStringReader
from fparser.two.parser import ParserFactory
import json
import re

#from werkzeug.utils import secure_filename
import magic
import rules


app = Flask(__name__, template_folder='templates')
#app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '0a8c0962d7dcb75977790884b868560c6f5f95dbf44b6d75e920d32d89bd7662')
#csrf = CSRFProtect(app)
app.config['UPLOAD_EXTENSIONS'] = ['.f90', '.f95', '.f03', '.f08', '.f', '.for', '.f77']
#app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024  # 512 kbytes


# Security - configurations for file upload
#
UPLOAD_FOLDER = '~/temp/uploads'
ALLOWED_EXTENSIONS = {'f90', 'f95', 'f03', 'f08', 'f', 'for', 'f77'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# mine type validation for file upload, only text/plain and application/octet-stream are allowed
def allowed_mime_type(file):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file.read(1024))
    file.seek(0)  # Reset the file pointer to the beginning
    return mime_type in {'text/plain', 'application/octet-stream'}

class Analyzer:
    def __init__(self):
        self.rules = []
        self.report = {"total_rules": 0, "passed_rules": 0, "failed_rules": 0, "details": {}}

    def add_rule(self, name, rule):
        self.rules.append((name, rule))
        self.report["total_rules"] += 1

    def analyze(self, nodes, fortran_code):
        for name, rule in self.rules:
            if name == "check undeclared variables":
                # This rule operates on the entire list of nodes
                result = rule(nodes, line_number)
            elif name == "check indentation":
                result = rule(fortran_code)
            else:
                # These rules operate on individual nodes
                result = None
                for line_number, node in enumerate(nodes, start=1):
                    result = rule(node, line_number)
                    if result:
                        break  # Stop checking if a rule fails for any node

            if result:
                self.report["failed_rules"] += 1
                self.report["details"][name] = result
            else:
                self.report["passed_rules"] += 1

    def generate_report(self, format="text"):
        if format == "json":
            return jsonify(self.report)
        else:
            return self._generate_text_report()

    def _generate_text_report(self) -> str:
        report_text = []
        report_text.append("=" * 50)
        report_text.append("Fortran Code Compliance Report")
        report_text.append("=" * 50)
        report_text.append(f"Totasdaal Rules: {self.report['total_rules']}")
        report_text.append(f"Passed Rules: {self.report['passed_rules']}")
        report_text.append(f"Failed Rules: {self.report['failed_rules']}")
        report_text.append("\nDetails:\n")
        report_text.append("=" * 50)
      
        for rule_name, details in self.report["details"].items():
            report_text.append(f"{rule_name}: {details}")
        
        report_text.append("=" * 50)

        return "\n".join(report_text)

def clean_fortran_code(file):
    """
    Remove diretivas de pré-compilação, MPI e OpenMP de um código Fortran.
    """
    #  
    fortran_code = file.read().decode("utf-8")
    lines = fortran_code.readlines()
    
    cleaned_lines = []
    
    for line in lines:
        stripped_line = line.strip()
        
        # Remover diretivas de pré-compilação
        if stripped_line.startswith("#ifdef"):
            continue
        
        # Remover diretivas OpenMP (!OMP, C$OMP, *$OMP)
        if re.match(r"^(!|C|\*)\$OMP", stripped_line, re.IGNORECASE):
            continue
        
        # Remover uso de MPI (importação do módulo MPI)
        if re.match(r"^\s*USE\s+MPI", stripped_line, re.IGNORECASE):
            continue
        
        cleaned_lines.append(line)
    
    return "".join(cleaned_lines)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        extension_error = rules.check_file_extension(file.filename)
        if extension_error:
            return jsonify({"error": extension_error}), 400
        # Security - check if file is allowed
        if not allowed_mime_type(file):
            return jsonify({"error": "Invalid file type"}), 400

        # Security - save file in secure way
        # filename = secure_filename(file.filename)
        # unique_filename = f"{uuid.uuid4().hex}_{filename}"
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        # file.save(file_path)
        # with open(file_path, "rb") as file:

        try:
            fortran_code = file.read().decode("utf-8")
            #fortran_code = clean_fortran_code(file)
        except Exception as e:
            return jsonify({"error": f"Error reading file: {str(e)}"}), 400

        try:
            fortran_version = request.form.get("fortran_version", "f2003")
            reader = FortranStringReader(fortran_code)
            parser = ParserFactory().create(std=fortran_version)
            # f2003 para Fortran 2003.
            # f2008 para Fortran 2008.
            # f2018 para Fortran 2018.
            parse_tree = parser(reader)
        except Exception as e:
            return jsonify({"error": f"Error parsing Fortran code: {str(e)}"}), 400

        nodes = [{"content": str(line).strip()} for line in parse_tree.content]

        analyzer = Analyzer()
        analyzer.add_rule("implicit_none", rules.check_implicit_none)
        analyzer.add_rule("lowercase", rules.check_lowercase)
        analyzer.add_rule("variable_declaration", rules.check_variable_declaration)
        analyzer.add_rule("obsolete_clauses", rules.check_obsolete_clauses)
        analyzer.add_rule("check undeclared variables", rules.check_undeclared_variables)
        analyzer.add_rule("check indentation", rules.check_indentation)


        analyzer.analyze(nodes,fortran_code)

        # Save report in temp file
        report_path = "/tmp/analyzer_report.json"
        #in production change report_path to /tmp/analyzer_report.json
        #report_path = "/tmp/analyzer_report.json"

        with open(report_path, "w") as report_file:
            json.dump(analyzer.report, report_file)

        return jsonify(analyzer.report)

    return render_template("index.html")

@app.route("/download_report")
def download_report():
    report_path = "/tmp/analyzer_report.json"
    #in production change report_path to /tmp/analyzer_report.json
    #report_path = "/tmp/analyzer_report.json"

    try: 
        @after_this_request
        def remove_file(response):
            try:
                os.remove(report_path)
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response
    #return send_file(report_path, as_attachment=True, attachment_filename="analyzer_report.json")
        return send_file(report_path, as_attachment=True, download_name="analyzer_report.json")

    except FileNotFoundError:
        return jsonify({"error": "Report file not found. Please analyze again."}), 404

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File is too large. Maximum file size is 500 KB."}), 413

# Security 
# Adds HTTP security headers to the response to protect against
# clickjacking and cross-site scripting (XSS) attacks.
@app.after_request
def set_secure_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == "__main__":
    app.run(debug=True)