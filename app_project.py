import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def setup_database():
    """Create database and tables with sample data"""
    conn = sqlite3.connect("student_activity.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        usn TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        branch TEXT NOT NULL,
        sem INT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS semesters (
        semester_id INTEGER PRIMARY KEY AUTOINCREMENT,
        usn TEXT NOT NULL,
        sem_number INTEGER NOT NULL,
        sgpa FLOAT,
        FOREIGN KEY (usn) REFERENCES students(usn)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        sem INT NOT NULL,
        branch TEXT,
        credits INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
        semester_id INTEGER NOT NULL,
        subject_code TEXT NOT NULL,
        cie INTEGER,
        see INTEGER,
        total INTEGER,
        grade TEXT,
        FOREIGN KEY (semester_id) REFERENCES semesters(semester_id),
        FOREIGN KEY (subject_code) REFERENCES subjects(code)
    )
    """)
    
    subjects_data = [
        ('23MA1BSMCS', 'Mathematical Foundation For CS Stream-1', 1, 'Information Science And Engineering', 4),
        ('22PH1BSPCS', 'Applied Physics for Computer Science Cluster', 1, 'Information Science And Engineering', 4),
        ('22CS1ESPOP', 'Principles of programming in C', 1, 'Information Science And Engineering', 3),
        ('22EC1ESIEL', 'Introduction to Electronics Engineering', 1, 'Information Science And Engineering', 3),
        ('22ME1AEIDT', 'Innovation and Design Thinking', 1, 'Information Science And Engineering', 1),
        ('22MA1HSBAK', 'Balake Kannada', 1, 'Information Science And Engineering', 1),
        ('22CS1ESPYP', 'Introduction to PYTHON Programming', 1, 'Information Science And Engineering', 3),
        ('22MA1AECEN', 'Communicative English', 1, 'Information Science And Engineering', 1),
        
        ('23MA2BSMCS', 'Mathematical Foundation For CS Stream-2', 2, 'Information Science And Engineering', 4),
        ('22CY2BSCCS', 'Applied Chemistry for Computer Science Engineering Stream', 2, 'Information Science And Engineering', 4),
        ('22ME2ESCED', 'Computer Aided Engineering Drawing', 2, 'Information Science And Engineering', 3),
        ('22ME2ESIME', 'Introduction to Mechanical Engineering', 2, 'Information Science And Engineering', 3),
        ('22EE2ESRES', 'Renewable Energy Sources', 2, 'Information Science And Engineering', 3),
        ('22MA2HSCIP', 'Constitution of India & Professional Ethics', 2, 'Information Science And Engineering', 1),
        ('23BT2AESFH', 'Scientific Foundations for Health', 2, 'Information Science And Engineering', 1),
        
        ('23MA3BSSDM', 'Statistics and Discrete Mathematics', 3, 'Information Science And Engineering', 3),
        ('23IS3PCCOA', 'Computer Organization and Architecture', 3, 'Information Science And Engineering', 3),
        ('23IS3PCDSC', 'Data Structures', 3, 'Information Science And Engineering', 4),
        ('23IS3PCOOP', 'Object oriented Programming Using C++', 3, 'Information Science And Engineering', 4),
        ('23IS3PCDLD', 'Digital Logic Design', 3, 'Information Science And Engineering', 3),
        ('23IS3PCOPS', 'Operating Systems', 3, 'Information Science And Engineering', 4),
        ('23IS3AEUSP', 'UNIX System Programming', 3, 'Information Science And Engineering', 1)
    ]
    
    for subject in subjects_data:
        cursor.execute("INSERT OR IGNORE INTO subjects (code, name, sem, branch, credits) VALUES (?, ?, ?, ?, ?)", subject)
    
    conn.commit()
    conn.close()

def calculate_sgpa(semester_id):
    """Calculate SGPA using credits and grade points formula"""
    conn = sqlite3.connect("student_activity.db")
    query = """
    SELECT m.grade, s.credits 
    FROM marks m 
    JOIN subjects s ON m.subject_code = s.code 
    WHERE m.semester_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(semester_id,))
    conn.close()
    
    grade_points = {'O': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 'F': 0}
    
    if df.empty:
        return 0
    
    total_points = sum(grade_points.get(row['grade'], 0) * row['credits'] for _, row in df.iterrows())
    total_credits = df['credits'].sum()
    
    return total_points / total_credits if total_credits > 0 else 0

st.title("🎓 Student Performance Visualization Tool")
st.markdown("**Advanced Python Course Project - Student Academic Performance Dashboard**")

setup_database()

# Sidebar
with st.sidebar:
    st.header("💯 Mode Selection")
    mode = st.radio("Choose Mode:", ["Personal Performance", "Student Comparison"])
    
    st.markdown("---")
    st.header("📊 Database Stats")
    conn = sqlite3.connect("student_activity.db")
    students_count = pd.read_sql_query("SELECT COUNT(*) as count FROM students", conn).iloc[0]['count']
    semesters_count = pd.read_sql_query("SELECT COUNT(*) as count FROM semesters", conn).iloc[0]['count']
    marks_count = pd.read_sql_query("SELECT COUNT(*) as count FROM marks", conn).iloc[0]['count']
    conn.close()
    
    st.metric("Students", students_count)
    st.metric("Semesters", semesters_count)
    st.metric("Marks Records", marks_count)

# Mode 1: Personal Performance
if mode == "Personal Performance":
    st.header("📈 Personal Performance Tracking")
    
    col1, col2 = st.columns(2)
    with col1:
        usn = st.text_input("Enter USN:", placeholder="e.g., 1BM23IS251").upper()
    with col2:
        name = st.text_input("Enter Name:", placeholder="Student Name")

    if usn and name:
        conn = sqlite3.connect("student_activity.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, sem FROM students WHERE usn = ?", (usn,))
        existing_student = cursor.fetchone()
        
        if existing_student:
            st.success(f"✅ Student {existing_student[0]} found!")
        else:
            current_sem = st.number_input("Current Semester:", min_value=1, max_value=8, value=4)
            if st.button("Add Student"):
                cursor.execute("INSERT INTO students (usn, name, branch, sem) VALUES (?, ?, ?, ?)", 
                              (usn, name, "Information Science And Engineering", current_sem))
                conn.commit()
                st.success(f"✅ Student {name} added!")
        
        current_sem = st.number_input("Current Semester (for visualization):", min_value=2, max_value=8, value=4)
        
        st.subheader("📝 Enter Marks for Previous Semesters")
        
        for sem in range(1, current_sem):
            with st.expander(f"Semester {sem}"):
                cursor.execute("SELECT semester_id FROM semesters WHERE usn = ? AND sem_number = ?", (usn, sem))
                existing_sem = cursor.fetchone()
                
                if existing_sem:
                    st.info(f"Data already exists for Semester {sem}")
                    continue
                
                cursor.execute("SELECT code, name, credits FROM subjects WHERE sem = ?", (sem,))
                subjects = cursor.fetchall()
                
                if subjects:
                    marks_data = []
                    
                    for subject_code, subject_name, credits in subjects:
                        st.write(f"**{subject_code}** - {subject_name} ({credits} credits)")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            cie = st.number_input("CIE (out of 50)", 0, 50, key=f"cie_{sem}_{subject_code}")
                        with col2:
                            see_input = st.number_input("SEE (out of 100)", 0, 100, key=f"see_{sem}_{subject_code}")
                        
                        see = see_input / 2
                        total = cie + see
                        
                        if total >= 90:
                            grade = 'O'
                        elif total >= 80:
                            grade = 'A+'
                        elif total >= 70:
                            grade = 'A'
                        elif total >= 60:
                            grade = 'B+'
                        elif total >= 50:
                            grade = 'B'
                        else:
                            grade = 'F'
                        
                        st.write(f"Total: {total:.1f} | Grade: {grade}")
                        marks_data.append((subject_code, cie, see, total, grade))
                    
                    if st.button(f"Save Semester {sem}", key=f"save_{sem}"):
                        cursor.execute("INSERT INTO semesters (usn, sem_number, sgpa) VALUES (?, ?, ?)", 
                                      (usn, sem, 0))
                        semester_id = cursor.lastrowid
                        
                        for subject_code, cie, see, total, grade in marks_data:
                            cursor.execute("INSERT INTO marks (semester_id, subject_code, cie, see, total, grade) VALUES (?, ?, ?, ?, ?, ?)",
                                          (semester_id, subject_code, cie, see, total, grade))
                        
                        conn.commit()
                        
                        sgpa = calculate_sgpa(semester_id)
                        cursor.execute("UPDATE semesters SET sgpa = ? WHERE semester_id = ?", (sgpa, semester_id))
                        conn.commit()
                        
                        st.success(f"✅ Semester {sem} saved! SGPA: {sgpa:.2f}")
                        st.rerun()
        
        st.subheader("📊 Performance Visualization")
        
        if st.button("Generate Graph"):
            query = "SELECT sem_number, sgpa FROM semesters WHERE usn = ? ORDER BY sem_number"
            df = pd.read_sql_query(query, conn, params=(usn,))
            
            if not df.empty:
                cgpa = df['sgpa'].mean()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(df['sem_number'], df['sgpa'], marker='o', linewidth=3, markersize=10, color='#1f77b4')
                    ax.axhline(y=cgpa, color='red', linestyle='--', linewidth=2, label=f'CGPA: {cgpa:.2f}')
                    
                    for i, row in df.iterrows():
                        ax.annotate(f'{row["sgpa"]:.2f}', (row['sem_number'], row['sgpa']), 
                                   textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold')
                    
                    ax.set_xlabel('Semester', fontsize=12)
                    ax.set_ylabel('SGPA', fontsize=12)
                    ax.set_title(f'Academic Performance - {name} ({usn})', fontsize=14, fontweight='bold')
                    ax.grid(True, alpha=0.3)
                    ax.legend(fontsize=12)
                    ax.set_ylim(0, 10)
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                    plt.close(fig)
                
                with col2:
                    st.write("**Performance Summary**")
                    st.metric("CGPA", f"{cgpa:.2f}")
                    best_sem = df.loc[df['sgpa'].idxmax(), 'sem_number']
                    st.metric("Best Semester", f"Sem {int(best_sem)}")
                    st.metric("Semesters Completed", len(df))
                
                # Semester-wise comparison
                st.subheader("📊 Semester-wise Subject Comparison")
                for sem_num in df['sem_number']:
                    with st.expander(f"Semester {int(sem_num)}"):
                        sem_marks_query = """
                        SELECT m.subject_code, m.total
                        FROM semesters s
                        JOIN marks m ON s.semester_id = m.semester_id
                        WHERE s.usn = ? AND s.sem_number = ?
                        ORDER BY m.subject_code
                        """
                        sem_marks = pd.read_sql_query(sem_marks_query, conn, params=(usn, sem_num))
                        
                        if not sem_marks.empty:
                            sem_comparison = []
                            for _, row in sem_marks.iterrows():
                                branch_avg_query = """
                                SELECT AVG(m.total) as branch_avg
                                FROM semesters s
                                JOIN marks m ON s.semester_id = m.semester_id
                                WHERE m.subject_code = ? AND s.sem_number = ?
                                """
                                branch_avg = pd.read_sql_query(branch_avg_query, conn, params=(row['subject_code'], sem_num))
                                if not branch_avg.empty and branch_avg.iloc[0]['branch_avg'] is not None:
                                    sem_comparison.append({
                                        'Subject': row['subject_code'][:10],
                                        'Student': row['total'],
                                        'Branch_Avg': branch_avg.iloc[0]['branch_avg']
                                    })
                            
                            if sem_comparison:
                                sem_comp_df = pd.DataFrame(sem_comparison)
                                
                                fig, ax = plt.subplots(figsize=(10, 5))
                                x = range(len(sem_comp_df))
                                width = 0.35
                                
                                ax.bar([i - width/2 for i in x], sem_comp_df['Student'], width, label='Student', color='#2ecc71')
                                ax.bar([i + width/2 for i in x], sem_comp_df['Branch_Avg'], width, label='Branch Avg', color='#e74c3c')
                                
                                ax.set_xlabel('Subjects', fontsize=11)
                                ax.set_ylabel('Total Marks', fontsize=11)
                                ax.set_title(f'Semester {int(sem_num)} - Subject Comparison', fontsize=12, fontweight='bold')
                                ax.set_xticks(x)
                                ax.set_xticklabels(sem_comp_df['Subject'], rotation=45, ha='right')
                                ax.legend()
                                ax.grid(True, alpha=0.3, axis='y')
                                plt.tight_layout()
                                
                                st.pyplot(fig)
                                plt.close(fig)
                

            else:
                st.warning("⚠️ No semester data found! Please enter marks first.")
        
        conn.close()
    else:
        st.info("👆 Enter USN and Name to get started!")

# Mode 2: Student Comparison
else:
    st.header("🔄 Student Comparison (Same Branch)")
    
    conn = sqlite3.connect("student_activity.db")
    
    # Get all students for remove dropdown
    all_students_temp = pd.read_sql_query("SELECT DISTINCT usn, name FROM students ORDER BY usn", conn)
    
    # Remove student option
    if len(all_students_temp) > 0:
        st.subheader("🗑️ Remove Student")
        student_to_remove = st.selectbox("Select student to remove:", all_students_temp['usn'].tolist())
        
        if st.button("❌ Remove Student"):
            cursor = conn.cursor()
            
            cursor.execute("SELECT semester_id FROM semesters WHERE usn = ?", (student_to_remove,))
            semester_ids = [row[0] for row in cursor.fetchall()]
            
            for sem_id in semester_ids:
                cursor.execute("DELETE FROM marks WHERE semester_id = ?", (sem_id,))
            
            cursor.execute("DELETE FROM semesters WHERE usn = ?", (student_to_remove,))
            cursor.execute("DELETE FROM students WHERE usn = ?", (student_to_remove,))
            
            conn.commit()
            st.success(f"✅ Student {student_to_remove} removed!")
            st.rerun()
        
        st.markdown("---")
    
    # Re-query students who have semester data (fresh data)
    all_students = pd.read_sql_query("""
        SELECT DISTINCT s.usn, s.name 
        FROM students s 
        JOIN semesters sem ON s.usn = sem.usn 
        ORDER BY s.usn
    """, conn)
    
    if len(all_students) > 1:
        # SGPA per semester comparison
        st.subheader("📊 SGPA Comparison per Semester")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for _, student in all_students.iterrows():
            sgpa_query = "SELECT sem_number, sgpa FROM semesters WHERE usn = ? ORDER BY sem_number"
            sgpa_data = pd.read_sql_query(sgpa_query, conn, params=(student['usn'],))
            if not sgpa_data.empty:
                ax.plot(sgpa_data['sem_number'], sgpa_data['sgpa'], marker='o', linewidth=2, markersize=8, label=student['usn'])
        
        ax.set_xlabel('Semester', fontsize=12)
        ax.set_ylabel('SGPA', fontsize=12)
        ax.set_title('SGPA Comparison Across Semesters', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 10)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        
        # CGPA per semester comparison
        st.subheader("📊 CGPA Comparison per Semester")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for _, student in all_students.iterrows():
            sgpa_query = "SELECT sem_number, sgpa FROM semesters WHERE usn = ? ORDER BY sem_number"
            sgpa_data = pd.read_sql_query(sgpa_query, conn, params=(student['usn'],))
            if not sgpa_data.empty:
                cgpa_per_sem = []
                for i in range(len(sgpa_data)):
                    cgpa = sgpa_data.iloc[:i+1]['sgpa'].mean()
                    cgpa_per_sem.append(cgpa)
                ax.plot(sgpa_data['sem_number'], cgpa_per_sem, marker='o', linewidth=2, markersize=8, label=student['usn'])
        
        ax.set_xlabel('Semester', fontsize=12)
        ax.set_ylabel('CGPA', fontsize=12)
        ax.set_title('CGPA Comparison Across Semesters', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 10)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        
        # Summary table
        st.subheader("📊 Overall Summary")
        summary_data = []
        for _, student in all_students.iterrows():
            cgpa_query = "SELECT AVG(sgpa) as cgpa FROM semesters WHERE usn = ?"
            cgpa_result = pd.read_sql_query(cgpa_query, conn, params=(student['usn'],))
            
            cie_query = "SELECT AVG(m.cie) as avg_cie FROM semesters s JOIN marks m ON s.semester_id = m.semester_id WHERE s.usn = ?"
            cie_result = pd.read_sql_query(cie_query, conn, params=(student['usn'],))
            
            if not cgpa_result.empty and not cie_result.empty:
                summary_data.append({
                    'USN': student['usn'],
                    'Name': student['name'],
                    'CGPA': cgpa_result.iloc[0]['cgpa'],
                    'Avg CIE': cie_result.iloc[0]['avg_cie']
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data).sort_values('CGPA', ascending=False)
            st.dataframe(summary_df, use_container_width=True)
    else:
        st.info("Add more students to see comparison charts!")
    
    conn.close()

st.markdown("---")
st.markdown("**🎓 Advanced Python Course Project | Student Performance Visualization Tool**")
