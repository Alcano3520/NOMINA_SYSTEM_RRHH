# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Development Commands

### Running the Application
```bash
# Run the main SAI payroll system
cd sai-nomina-tkinter
python main.py

# Install dependencies
pip install -r requirements.txt
```

### Database Setup
```bash
# Initialize database (automatic on first run)
python -c "from database.initialize import initialize_database; initialize_database()"
```

### Common Development Tasks
```bash
# Check dependencies
python main.py  # Will automatically check and report missing dependencies

# Create reports directory
python -c "from config import Config; Config.create_directories()"
```

## 🏗️ Architecture Overview

This repository contains a comprehensive HR and Payroll Management System for Ecuador, built with Python/Tkinter. The main application is in the `sai-nomina-tkinter/` directory.

### High-Level Structure
```
sai-nomina-tkinter/
├── database/          # SQLAlchemy ORM models and database initialization
├── gui/
│   ├── components/    # Reusable UI components (StatCard, DataTable, etc.)
│   ├── modules/       # Business logic modules (employees, payroll, etc.)
│   └── main_window.py # Main application window
├── services/          # Business logic and data processing
├── utils/             # Ecuadorian-specific calculations and validations
├── config.py          # Application configuration and constants
└── main.py           # Application entry point
```

### Key Business Modules
The system includes 7 main functional modules:
- **Empleados**: Employee management with Ecuadorian ID validation
- **Nómina**: Payroll processing with Ecuador-specific calculations
- **Décimos**: 13th and 14th salary management
- **Vacaciones**: Vacation tracking (15 days annual)
- **Préstamos**: Employee loan management
- **Dotación**: Uniform and equipment tracking
- **Reportes**: Executive dashboard and PDF reports

### Database Architecture
Uses SQLAlchemy ORM with SQLite database. Main entities:
- `Empleado`: Employee records with Ecuador-specific validations
- `RolPago`: Payroll records with automatic calculations
- `Decimo`: 13th/14th salary management
- `Vacacion`: Vacation requests and tracking
- `Prestamo`: Employee loans and deductions
- `Dotacion`: Equipment and uniform assignments

## 🇪🇨 Ecuador-Specific Features

### Legal Compliance
The system implements Ecuador's labor law requirements:
- **IESS Contributions**: 9.45% employee, 11.15% employer
- **Reserve Funds**: 8.33% after 1 year of employment
- **13th Salary**: Annual income / 12
- **14th Salary**: Proportional to minimum wage ($460 SBU)
- **Overtime**: 25%, 50%, 100% rates based on time/day
- **Vacation**: 15 days annual entitlement

### Validations
- Ecuadorian ID (cédula) validation with verification digit
- Business RUC validation
- Minimum salary enforcement (SBU = $460)
- IESS contribution calculations
- Proper date range validations

### Data Processing
- Excel/CSV import functionality for bulk operations
- PDF report generation with professional formatting
- Automatic calculation of all payroll components
- Real-time validation of Ecuadorian regulations

## 🎨 UI Architecture

### Component System
Built with reusable Tkinter components:
- **StatCard**: Dashboard metrics cards
- **DataTable**: Sortable data tables with actions
- **SearchForm**: Dynamic search forms
- **ModernButton**: Styled buttons with hover effects

### Design System
- **Colors**: Professional blue gradient theme (`Config.COLORS`)
- **Fonts**: Segoe UI family with size hierarchy (`Config.FONTS`)
- **Layout**: Card-based design with consistent spacing
- **Navigation**: Sidebar navigation with module icons

### Styling Approach
- Modern flat design with subtle shadows
- Responsive layout within fixed window size
- Consistent spacing and typography
- Professional color scheme suitable for business use

## 🔧 Technical Standards

### Code Organization
- **MVC Pattern**: Clear separation of models, views, and controllers
- **Configuration**: Centralized in `config.py` with Ecuador-specific constants
- **Error Handling**: Comprehensive logging and user-friendly error messages
- **Documentation**: Spanish comments for business logic, English for technical code

### Development Practices
- **Dependencies**: Listed in `requirements.txt` with version constraints
- **Database**: SQLAlchemy ORM with automatic schema creation
- **Logging**: Structured logging to daily log files
- **Validation**: Real-time input validation with Ecuador-specific rules

### Performance Considerations
- **Database**: SQLite for simplicity and portability
- **UI**: Responsive design with efficient data loading
- **Memory**: Proper resource management for large datasets
- **Calculations**: Optimized payroll processing for hundreds of employees

## 📋 Important Notes

### System Requirements
- Python 3.8+ required
- Windows/Linux/macOS compatible
- No external database server needed (SQLite)
- GUI uses native Tkinter (no additional GUI frameworks)

### Business Context
- **Target**: Security companies in Ecuador (INSEVIG CIA. LTDA.)
- **Scale**: 100-200 employees (primarily security guards)
- **Compliance**: Full Ecuador labor law compliance
- **Usage**: Desktop application for HR/Payroll departments

### Development Priority
When making changes, prioritize:
1. **Legal Compliance**: Ecuador labor law requirements
2. **Data Accuracy**: Payroll calculations must be precise
3. **User Experience**: Simple, intuitive interface for HR staff
4. **Performance**: Handle hundreds of employees efficiently
5. **Reliability**: Robust error handling and data validation