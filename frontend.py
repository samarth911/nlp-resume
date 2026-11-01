import streamlit as st
import requests

st.title("AI Recruitment System - Offline NLP")

menu = st.sidebar.selectbox("Menu",
        ["Upload Resume","Match with JD","Bulk Ranking"])


# ========== UPLOAD ==========

if menu == "Upload Resume":

    file = st.file_uploader("Upload PDF/DOCX")

    if file and st.button("Submit"):

        res = requests.post(
            "http://localhost:8000/upload_resume",
            files={"file": file}
        )

        data = res.json()

        st.session_state["resume"] = data["resume"]

        st.success("Resume Loaded Successfully")


# ========== MATCH ==========

if menu == "Match with JD":

    if "resume" not in st.session_state:
        st.warning("First upload resume")
    else:
        st.text_area("Resume Text",
                     st.session_state["resume"],
                     height=200)

                # ----- JOB DESCRIPTION INPUT -----

        jd_text = st.text_area("Paste Job Description (Optional)")

        jd_file = st.file_uploader("Upload JD PDF (Optional)", key="jd")

        if jd_file:
            res = requests.post(
                "http://localhost:8000/upload_resume",
                files={"file": jd_file}
            )
            jd_text = res.json()["resume"]
            st.success("JD PDF Loaded")


        if st.button("Analyze"):

            res = requests.post(
                "http://localhost:8000/match",
                json={
                    "resume": st.session_state["resume"],
                    "jd": jd_text
                }
            )

            result = res.json()

                        # ===== CANDIDATE DETAILS =====
            st.subheader("Candidate Details")

            st.write("**Name:**", result["name"])
            st.write("**Email:**", result["email"])
            st.write("**Phone:**", result["phone"])

            # ===== ATS SCORE =====
            st.subheader("ATS Score")
            st.write(result["ATS_Score"])

            # ===== CLICKABLE EMAIL IF SCORE > 70 =====
            if result["ATS_Score"] >= 70 and result["email"] != "Not Found":

                mailto = f"mailto:{result['email']}?subject=Interview Shortlist&body=Congratulations, you have been shortlisted."

                st.markdown(
                    f'''
                    <a href="{mailto}" target="_blank">
                    <button style="
                        background:#28a745;
                        color:white;
                        padding:10px;
                        border:none;
                        border-radius:6px;
                        cursor:pointer;">
                        Email Candidate
                    </button>
                    </a>
                    ''',
                    unsafe_allow_html=True
                )

            # ===== SKILLS =====
            st.subheader("Matching Skills")
            st.write(result["matching_skills"])

            st.subheader("Missing Skills")
            st.write(result["missing_skills"])

# ========== BULK RANKING ==========

if menu == "Bulk Ranking":

    st.header("Bulk Resume Ranking")
    st.write("Upload multiple resumes and compare them with multiple Job Descriptions")

    # Multiple resume uploader
    files = st.file_uploader(
        "Upload Multiple Resumes (PDF/DOCX)",
        accept_multiple_files=True,
        type=["pdf", "docx"]
    )

    # Store resumes in session_state
    if files:
        if "resumes" not in st.session_state:
            st.session_state["resumes"] = []
            st.session_state["processed_files"] = []
        
        # Check if new files were uploaded
        current_file_names = [f.name for f in files]
        if current_file_names != st.session_state.get("processed_files", []):
            st.session_state["resumes"] = []
            st.session_state["processed_files"] = current_file_names
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, file in enumerate(files):
                status_text.text(f"Processing {file.name}... ({idx+1}/{len(files)})")
                res = requests.post(
                    "http://localhost:8000/upload_resume",
                    files={"file": file}
                )
                if res.status_code == 200:
                    st.session_state["resumes"].append(res.json()["resume"])
                progress_bar.progress((idx + 1) / len(files))
            
            status_text.text(f"✓ Successfully loaded {len(st.session_state['resumes'])} resumes")
            progress_bar.empty()
            status_text.empty()

        if st.session_state.get("resumes"):
            st.success(f"✓ {len(st.session_state['resumes'])} resumes loaded")

    # Job Description Input - Multiple JDs
    st.subheader("Job Descriptions")
    
    # Initialize session_state for JDs
    if "jds" not in st.session_state:
        st.session_state["jds"] = []
    
    # Option 1: Text input for JDs
    st.write("**Option 1: Enter Job Descriptions as Text**")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        jd_name_input = st.text_input(
            "JD Name/Title (Optional)",
            key="jd_name_input",
            placeholder="e.g., Frontend Developer"
        )
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
    
    jd_text_input = st.text_area(
        "Paste Job Description (Text)",
        height=150,
        placeholder="Enter job description text here...",
        key="jd_text_input"
    )
    
    if jd_text_input and jd_text_input.strip():
        # Add JD from text input
        if st.button("Add JD from Text", key="add_jd_text"):
            jd_name = jd_name_input.strip() if jd_name_input and jd_name_input.strip() else f"JD {len(st.session_state.get('jds', [])) + 1}"
            
            if "jds" not in st.session_state:
                st.session_state["jds"] = []
            
            st.session_state["jds"].append({
                "name": jd_name,
                "text": jd_text_input.strip()
            })
            st.success(f"✓ Added JD: {jd_name}")
            st.rerun()
    
    # Option 2: Multiple JD PDF uploads
    st.write("**Option 2: Upload JD PDFs**")
    jd_files = st.file_uploader(
        "Upload Multiple JD PDFs",
        accept_multiple_files=True,
        type=["pdf"],
        key="jd_upload_multiple"
    )
    
    # Store JDs in session_state from PDF uploads
    if jd_files:
        if "processed_jd_files" not in st.session_state:
            st.session_state["processed_jd_files"] = []
        
        # Check if new JD files were uploaded
        current_jd_file_names = [f.name for f in jd_files]
        if current_jd_file_names != st.session_state.get("processed_jd_files", []):
            # Process new JD files
            new_jds = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, jd_file in enumerate(jd_files):
                status_text.text(f"Processing JD: {jd_file.name}... ({idx+1}/{len(jd_files)})")
                try:
                    jd_file.seek(0)
                    file_bytes = jd_file.read()
                    jd_file.seek(0)
                    
                    res = requests.post(
                        "http://localhost:8000/upload_resume",
                        files={"file": (jd_file.name, file_bytes, "application/pdf")},
                        timeout=30
                    )
                    
                    if res.status_code == 200:
                        response_data = res.json()
                        if "error" not in response_data:
                            jd_text = response_data.get("resume", "")
                            if jd_text and jd_text.strip():
                                jd_name = jd_file.name.replace(".pdf", "").replace("_", " ").title()
                                new_jds.append({
                                    "name": jd_name,
                                    "text": jd_text
                                })
                except Exception as e:
                    st.error(f"Error processing {jd_file.name}: {str(e)}")
                progress_bar.progress((idx + 1) / len(jd_files))
            
            # Add new JDs to session_state (avoid duplicates)
            existing_jd_names = [jd["name"] for jd in st.session_state.get("jds", [])]
            added_count = 0
            for new_jd in new_jds:
                if new_jd["name"] not in existing_jd_names:
                    st.session_state["jds"].append(new_jd)
                    added_count += 1
            
            st.session_state["processed_jd_files"] = current_jd_file_names
            if added_count > 0:
                status_text.text(f"✓ Successfully loaded {added_count} JD(s)")
                progress_bar.empty()
                status_text.empty()
                st.success(f"✓ Successfully loaded {added_count} JD(s)")
                st.rerun()
    
    # Display loaded JDs
    if st.session_state.get("jds") and len(st.session_state["jds"]) > 0:
        st.write(f"**Loaded JDs:** {len(st.session_state['jds'])}")
        for idx, jd in enumerate(st.session_state["jds"], 1):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{idx}. {jd['name']}")
            with col2:
                if st.button("Remove", key=f"remove_jd_{idx}"):
                    st.session_state["jds"].pop(idx - 1)
                    st.rerun()
    elif not st.session_state.get("jds") or len(st.session_state.get("jds", [])) == 0:
        st.info("ℹ️ No JDs loaded yet. Add JDs using the options above.")

    # Rank Candidates Button
    if st.button("Rank Candidates", type="primary"):
        
        if "resumes" not in st.session_state or len(st.session_state["resumes"]) == 0:
            st.error("Please upload at least one resume")
        elif "jds" not in st.session_state or len(st.session_state["jds"]) == 0:
            st.error("Please add at least one Job Description")
        else:
            with st.spinner("Ranking candidates for all JDs..."):
                res = requests.post(
                    "http://localhost:8000/bulk_match",
                    json={
                        "resumes": st.session_state["resumes"],
                        "jds": st.session_state["jds"]
                    }
                )

                if res.status_code == 200:
                    result = res.json()
                    
                    # Display results for each JD
                    for jd_result in result.get("results", []):
                        jd_name = jd_result.get("jd_name", "Unknown JD")
                        ranking = jd_result.get("ranking", [])
                        
                        if ranking:
                            st.divider()
                            st.subheader(f"📋 {jd_name}")
                            
                            # Create table data
                            table_data = []
                            for idx, candidate in enumerate(ranking, 1):
                                table_data.append({
                                    "Rank": idx,
                                    "Name": candidate.get("name", "N/A"),
                                    "Email": candidate.get("email", "Not Found"),
                                    "Phone": candidate.get("phone", "Not Found"),
                                    "Score": f"{candidate.get('score', 0):.2f}",
                                    "Matching Skills": ", ".join(candidate.get("matching_skills", [])) if candidate.get("matching_skills") else "None"
                                })

                            # Display table
                            st.dataframe(
                                table_data,
                                use_container_width=True,
                                hide_index=True
                            )

                            # Display detailed results with email buttons
                            with st.expander(f"View Detailed Results for {jd_name}"):
                                for idx, candidate in enumerate(ranking, 1):
                                    with st.expander(f"#{idx} - {candidate.get('name', 'N/A')} (Score: {candidate.get('score', 0):.2f})"):
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.write("**Email:**", candidate.get("email", "Not Found"))
                                            st.write("**Phone:**", candidate.get("phone", "Not Found"))
                                            st.write("**ATS Score:**", f"{candidate.get('score', 0):.2f}")
                                        
                                        with col2:
                                            st.write("**Matching Skills:**")
                                            skills = candidate.get("matching_skills", [])
                                            if skills:
                                                st.write(", ".join(skills))
                                            else:
                                                st.write("None")

                                        # Clickable email button for score > 70
                                        if candidate.get("score", 0) >= 70 and candidate.get("email", "Not Found") != "Not Found":
                                            email = candidate.get("email")
                                            mailto = f"mailto:{email}?subject=Interview Shortlist - {jd_name}&body=Congratulations, you have been shortlisted for the position: {jd_name}."
                                            
                                            st.markdown(
                                                f'''
                                                <a href="{mailto}" target="_blank">
                                                <button style="
                                                    background:#28a745;
                                                    color:white;
                                                    padding:10px 20px;
                                                    border:none;
                                                    border-radius:6px;
                                                    cursor:pointer;
                                                    font-size:14px;
                                                    margin-top:10px;">
                                                    📧 Email Candidate
                                                </button>
                                                </a>
                                                ''',
                                                unsafe_allow_html=True
                                            )
                        else:
                            st.warning(f"No candidates found for {jd_name}")
                else:
                    st.error(f"Error: {res.status_code} - {res.text}")
