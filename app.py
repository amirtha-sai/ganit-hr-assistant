import streamlit as st
import requests
import json

# =====================================================
# CONFIG
# =====================================================

API_URL = "https://dtl1p82dzl.execute-api.us-east-1.amazonaws.com/dev/chat"

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🤖 HR Assistant")

    employee_id = st.text_input(
        "Employee ID",
        value="EMP001"
    )

    st.markdown("---")

    st.markdown("""
    ### Features

    ✅ HR Policy Q&A  
    ✅ Leave Policy Search  
    ✅ Reimbursement Guidance  
    ✅ Semantic Search  
    ✅ Claude AI Answers  
    ✅ Policy Citations  
    ✅ Vector Search
    """)

    st.markdown("---")

    st.caption("Powered by AWS Bedrock + OpenSearch")

# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================================================
# HEADER
# =====================================================

st.title("🎯 HR Policy Assistant")

st.caption(
    "Ask questions about leave policy, reimbursement, benefits, conduct, travel, POSH, and more."
)

# =====================================================
# DISPLAY CHAT HISTORY
# =====================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# =====================================================
# USER INPUT
# =====================================================

question = st.chat_input(
    "Ask an HR policy question..."
)

# =====================================================
# PROCESS QUESTION
# =====================================================

if question:

    # -------------------------------------------------
    # USER MESSAGE
    # -------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # -------------------------------------------------
    # ASSISTANT RESPONSE
    # -------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Searching HR policies..."):

            try:

                payload = {
                    "question": question,
                    "employee_id": employee_id
                }

                response = requests.post(
                    API_URL,
                    json=payload
                )

                # -------------------------------------------------
                # PARSE RESPONSE
                # -------------------------------------------------

                result = response.json()

                # Lambda may wrap response inside "body"
                if "body" in result:

                    if isinstance(result["body"], str):
                        result = json.loads(result["body"])
                    else:
                        result = result["body"]

                # -------------------------------------------------
                # EXTRACT DATA
                # -------------------------------------------------

                answer = result.get(
                    "answer",
                    "No answer returned."
                )

                citations = result.get(
                    "citations",
                    []
                )

                # -------------------------------------------------
                # DISPLAY ANSWER
                # -------------------------------------------------

                st.markdown(answer)

                # -------------------------------------------------
                # DISPLAY CITATIONS
                # -------------------------------------------------

                if len(citations) > 0:

                    st.markdown("---")
                    st.markdown("## 📚 Policy Sources")

                    for citation in citations:

                        chunk_number = citation.get(
                            "chunk_number",
                            "N/A"
                        )

                        policy_name = citation.get(
                            "policy_name",
                            "Unknown Policy"
                        )

                        page = citation.get(
                            "page",
                            "N/A"
                        )

                        section = citation.get(
                            "section",
                            "N/A"
                        )

                        score = citation.get(
                            "score",
                            0
                        )

                        text = citation.get(
                            "text",
                            ""
                        )

                        # -----------------------------------------
                        # EXPANDABLE SOURCE CARD
                        # -----------------------------------------

                        with st.expander(
                            f"📄 Chunk {chunk_number} | {policy_name} | Score: {round(score, 3)}"
                        ):

                            st.markdown(f"""
                **Policy:** {policy_name}

                **Section:** {section}

                **Page:** {page}

                **Similarity Score:** {round(score, 3)}
                """)

                            st.markdown("---")

                            st.write(text)

                else:

                    st.info(
                        "No supporting policy chunks returned."
                    )
                # -------------------------------------------------
                # SAVE CHAT HISTORY
                # -------------------------------------------------

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                error_message = f"Error: {str(e)}"

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
