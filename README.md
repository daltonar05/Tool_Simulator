Tool Life Simulator
A modern web application to simulate tool life using uploaded data files, with secure user authentication, admin approval, result downloads, and a polished Bootstrap 5 interface.

🚀 Features
Simulate Tool Life: Upload data files, run simulations, and download results.

User Authentication: Register, login, and require admin approval before access.

Admin Panel: Approve users, manage admin roles, and oversee the user base.

Role Management: Grant/revoke admin rights and approve/unapprove users.

Session Security: Logout disables browser back navigation to protected pages.

Responsive UI: Built with Bootstrap 5 and FontAwesome for a professional look.

Standalone Executable: Easily package and distribute as a Windows .exe using PyInstaller.

Automatic Browser Launch: App opens in your default browser on startup.

🛠️ Tech Stack
Backend Framework: FastAPI

Database: SQLite (via SQLAlchemy ORM)

Templating Engine: Jinja2

Frontend: Bootstrap 5, FontAwesome

Authentication: Custom logic with registration, login, admin approval, and role management

Session Management: In-memory (per client IP)

File Handling: Upload files for simulation; results saved in /results and downloadable

Static Files: Served from /static (CSS, images)

tool_simulator_app/
├── main.py                  # Application entry point, mounts static, includes router, runs Uvicorn
├── Tool_simulator/
│   └── __init__.py          # FastAPI router: routes, user management, simulation logic
├── templates/               # Jinja2 HTML templates (index, login, register, admin, result, component_view)
├── static/                  # CSS, images, and static assets
├── admin.env                # Environment file with admin credentials
├── results/                 # Stores simulation output files (created automatically)
├── requirements.txt         # All required Python packages


Environment Variables: Loaded from admin.env using python-dotenv

📝 Requirements
Python 3.10 or 3.11 (recommended)

See requirements.txt for all dependencies, including:

fastapi

uvicorn

sqlalchemy

jinja2

python-dotenv

passlib[bcrypt]

bcrypt

openpyxl

PyInstaller (for packaging)
Packaging: PyInstaller for Windows executable

Excel Handling: openpyxl for reading/writing Excel files

Developed with ❤️ using FastAPI, Bootstrap 5, and the open-source Python ecosystem.
