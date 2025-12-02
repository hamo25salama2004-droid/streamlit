import streamlit as st
import time
import pickle
import os
from typing import Dict, Any, List

# --- 🛠️ الثوابت والإعدادات الأولية ---

# ملف حفظ البيانات
DATA_FILE = 'quiz_data.pkl'
# اسم المستخدم وكلمة المرور للإعدادات
ADMIN_USERNAME = '2025'
ADMIN_PASSWORD = '2026'
# إجمالي وقت الاختبار بالثواني
DEFAULT_QUIZ_TIME = 600  # 10 دقائق

# أنواع الأسئلة
QUESTION_TYPES = {
    "multiple_choice": "اختيار من متعدد",
    "true_false": "صواب أو خطأ",
    "essay": "مقالي"
}

# --- 🎨 التنسيق والمظهر الفاخر ---

def set_page_style():
    """يضيف تنسيقات CSS لتحسين المظهر."""
    st.set_page_config(page_title="نظام اختبارات ديناميكي", layout="wide", initial_sidebar_state="collapsed")
    
    st.markdown("""
        <style>
            /* إخفاء عناصر Streamlit الافتراضية */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* تنسيق الأزرار الرئيسية */
            div.stButton > button:first-child {
                background-color: #007BFF; /* أزرق جذاب */
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 20px;
                border: 3px solid #0056b3;
                transition: all 0.3s ease;
            }
            div.stButton > button:first-child:hover {
                background-color: #0056b3;
                border-color: #007BFF;
                transform: scale(1.02);
            }

            /* تنسيق العنوان */
            .main-header {
                font-size: 40px;
                color: #4CAF50; /* أخضر */
                text-align: center;
                margin-bottom: 20px;
                padding: 10px;
                border-bottom: 5px solid #4CAF50;
            }
            
            /* تنسيق صناديق الإدخال والنص */
            .stTextInput>div>div>input, .stTextArea>div>div>textarea {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
            
            /* تلوين النتيجة النهائية */
            .final-score {
                font-size: 36px;
                font-weight: bold;
                color: #FFC107; /* ذهبي */
                text-align: center;
                background-color: #262626;
                padding: 15px;
                border-radius: 10px;
            }
            
            /* تنسيق العداد الزمني */
            .time-counter {
                font-size: 28px;
                font-weight: bold;
                color: #DC3545; /* أحمر للخطر/الوقت */
                text-align: center;
                border: 3px dashed #DC3545;
                padding: 5px;
                border-radius: 5px;
            }
            
        </style>
        """, unsafe_allow_html=True)


# --- 💾 وظائف حفظ وتحميل البيانات ---

def load_data() -> Dict[str, Any]:
    """تحميل بيانات الأسئلة من الملف."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'rb') as f:
                data = pickle.load(f)
            # ضمان وجود المفاتيح
            data.setdefault('questions', [])
            data.setdefault('quiz_time', DEFAULT_QUIZ_TIME)
            return data
        except Exception:
            # في حال تلف الملف، نبدأ ببيانات فارغة
            return {'questions': [], 'quiz_time': DEFAULT_QUIZ_TIME}
    return {'questions': [], 'quiz_time': DEFAULT_QUIZ_TIME}

def save_data(data: Dict[str, Any]):
    """حفظ بيانات الأسئلة في الملف."""
    try:
        with open(DATA_FILE, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        st.error(f"خطأ في حفظ بيانات الاختبار: {e}")


# تهيئة الجلسة وتحميل البيانات
if 'data' not in st.session_state:
    st.session_state.data = load_data()
    st.session_state.logged_in = False
    st.session_state.current_page = 'main'
    st.session_state.quiz_in_progress = False

# --- 🔑 صفحة تسجيل الدخول (الإعدادات) ---

def login_page():
    """واجهة تسجيل الدخول للإعدادات."""
    st.markdown("<h2 style='text-align: center; color: #007BFF;'>🔑 تسجيل الدخول للإعدادات</h2>", unsafe_allow_html=True)
    st.markdown("---")

    col_back, col_spacer = st.columns([1, 4])
    with col_back:
        if st.button("العودة للصفحة الرئيسية", key="login_back"):
            st.session_state.current_page = 'main'
            st.rerun()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم (2025)", max_chars=4)
            password = st.text_input("كلمة المرور (2026)", type="password", max_chars=4)
            submit_button = st.form_submit_button("تسجيل الدخول", use_container_width=True)

            if submit_button:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.current_page = 'settings'
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

# --- ⚙️ صفحة الإعدادات (بعد تسجيل الدخول) ---

def render_add_question_form():
    """واجهة ديناميكية لإضافة سؤال بناءً على نوعه."""
    st.subheader("➕ إضافة سؤال جديد")

    # تحديد نوع السؤال
    question_type_label = st.selectbox(
        "اختر نوع السؤال:",
        list(QUESTION_TYPES.values()),
        key="q_type_select"
    )
    
    # الحصول على المفتاح بناءً على القيمة المختارة
    q_type_key = next(key for key, value in QUESTION_TYPES.items() if value == question_type_label)

    with st.form("add_question_form", clear_on_submit=True):
        st.markdown(f"#### إعداد سؤال من نوع: **{question_type_label}**")
        q_text = st.text_area("نص السؤال:", key="q_text_input")
        q_score = st.number_input("درجة السؤال:", min_value=1, value=5, key="q_score_input")
        
        # --- الحقول الخاصة بكل نوع سؤال ---
        correct_answer = None
        
        if q_type_key == "multiple_choice":
            st.info("أدخل 4 خيارات، وحدد الإجابة الصحيحة.")
            q_options = [
                st.text_input("الخيار 1:", key="opt_1"),
                st.text_input("الخيار 2:", key="opt_2"),
                st.text_input("الخيار 3:", key="opt_3"),
                st.text_input("الخيار 4:", key="opt_4"),
            ]
            options_labels = ["1", "2", "3", "4"]
            
            correct_index = st.selectbox("الإجابة الصحيحة هي:", options_labels, key="correct_mc")
            
            if correct_index:
                correct_answer = q_options[int(correct_index) - 1]

        elif q_type_key == "true_false":
            st.info("حدد ما إذا كانت العبارة صحيحة أم خاطئة.")
            correct_answer = st.radio("الإجابة الصحيحة:", ("صحيح", "خطأ"), key="correct_tf")
            
        elif q_type_key == "essay":
            st.info("الأسئلة المقالية تتطلب تصحيحًا يدويًا. الإجابة الصحيحة هنا هي الإجابة النموذجية.")
            correct_answer = st.text_area("الإجابة النموذجية:", key="correct_essay")
            
        # ---------------------------------
        
        add_button = st.form_submit_button("حفظ وإضافة السؤال", use_container_width=True)

        if add_button:
            if q_text and correct_answer and q_score > 0:
                # التحقق الإضافي لـ MC
                if q_type_key == "multiple_choice" and not all(q_options):
                    st.error("الرجاء ملء جميع خيارات الاختيار من متعدد.")
                    return
                
                new_question = {
                    'type': q_type_key,
                    'text': q_text,
                    'options': q_options if q_type_key == "multiple_choice" else None,
                    'correct_answer': correct_answer,
                    'score': q_score
                }
                st.session_state.data['questions'].append(new_question)
                save_data(st.session_state.data)
                st.success("✅ تم إضافة السؤال بنجاح!")
            else:
                st.error("الرجاء ملء نص السؤال والدرجة والإجابة الصحيحة.")

def settings_page():
    """واجهة إدارة الأسئلة وتعديل وقت الاختبار."""
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>⚙️ إعدادات مدير الاختبار</h2>", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("العودة للصفحة الرئيسية", key="settings_back"):
        st.session_state.current_page = 'main'
        st.rerun()
        return

    # 1. إدارة وقت الاختبار
    st.subheader("⏱️ إعداد وقت الاختبار الكلي")
    current_time_minutes = int(st.session_state.data.get('quiz_time', DEFAULT_QUIZ_TIME) / 60)
    
    col_time, col_button = st.columns([3, 1])
    with col_time:
        new_quiz_time_min = st.number_input(
            "وقت الاختبار (بالدقائق)",
            min_value=1,
            max_value=120,
            value=current_time_minutes,
            key="quiz_time_min_input"
        )
    with col_button:
        st.markdown("<br>", unsafe_allow_html=True) # تباعد لتنسيق الزر
        if st.button("تحديث الوقت", use_container_width=True):
            st.session_state.data['quiz_time'] = new_quiz_time_min * 60
            save_data(st.session_state.data)
            st.success(f"تم تحديث وقت الاختبار إلى {new_quiz_time_min} دقيقة.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 2. إضافة سؤال جديد
    render_add_question_form()

    st.markdown("---")

    # 3. عرض ومراجعة الأسئلة
    questions = st.session_state.data.get('questions', [])
    st.subheader(f"📝 قائمة الأسئلة الحالية ({len(questions)} سؤال)")
    
    if questions:
        for i, q in enumerate(questions):
            type_label = QUESTION_TYPES.get(q.get('type', ''))
            
            with st.expander(f"سؤال {i+1} | النوع: **{type_label}** | الدرجة: **{q.get('score', 0)}**"):
                st.markdown(f"**نص السؤال:** {q.get('text', 'لا يوجد نص')}")
                
                if q['type'] == 'multiple_choice' and q['options']:
                    st.write("الخيارات:")
                    for opt in q['options']:
                        # تمييز الإجابة الصحيحة
                        if opt == q['correct_answer']:
                            st.success(f"✔️ {opt}")
                        else:
                            st.write(f"• {opt}")
                
                elif q['type'] == 'true_false':
                    st.write(f"الإجابة الصحيحة: **{q['correct_answer']}**")
                    
                elif q['type'] == 'essay':
                    st.write(f"الإجابة النموذجية: *{q['correct_answer']}*")

                if st.button(f"حذف سؤال {i+1}", key=f"delete_{i}"):
                    st.session_state.data['questions'].pop(i)
                    save_data(st.session_state.data)
                    st.success(f"تم حذف السؤال {i+1}.")
                    st.rerun()
    else:
        st.info("لا توجد أسئلة مضافة حتى الآن.")

# --- 📝 صفحة حل الاختبار ---

def quiz_page():
    """واجهة عرض وحل الاختبار وحساب النتيجة."""
    questions = st.session_state.data.get('questions', [])
    total_time = st.session_state.data.get('quiz_time', DEFAULT_QUIZ_TIME)

    if not questions:
        st.warning("لا يوجد أسئلة حالياً. يرجى إضافة أسئلة من صفحة الإعدادات.")
        if st.button("العودة للصفحة الرئيسية", key="quiz_no_q_back"):
            st.session_state.current_page = 'main'
            st.rerun()
        return

    # بدء الاختبار ومنطق الوقت
    if not st.session_state.quiz_in_progress:
        st.session_state.quiz_in_progress = True
        st.session_state.start_time = time.time()
        # تهيئة إجابات المستخدم، بما في ذلك المقالي
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.show_results = False
        st.session_state.essay_scores = [None] * len(questions) # لتخزين درجات المقالي لاحقاً

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, total_time - elapsed_time)

    # placeholder لعرض العداد
    time_placeholder = st.empty()
    
    # ------------------
    # منطق تحديث الوقت
    # ------------------
    if not st.session_state.show_results:
        mins = int(remaining_time // 60)
        secs = int(remaining_time % 60)
        
        # عرض العداد بأسلوب مميز
        time_placeholder.markdown(f'<div class="time-counter">⏱️ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        
        if remaining_time <= 0:
            st.warning("🚫 انتهى الوقت! سيتم عرض النتيجة.")
            st.session_state.show_results = True
            st.rerun()
        else:
            # تحديث الواجهة كل ثانية لعمل العداد
            time.sleep(1)
            st.rerun()

    st.markdown("---")

    if st.session_state.show_results:
        # --- عرض النتيجة بعد انتهاء الاختبار ---
        st.markdown("<h2 style='text-align: center; color: #FFC107;'>🎉 نتيجة الاختبار</h2>", unsafe_allow_html=True)
        total_score = 0
        max_score = sum(q.get('score', 0) for q in questions)
        
        st.warning("ملاحظة: الأسئلة المقالية لم يتم تصحيحها تلقائياً وتتطلب مراجعة يدوية.")

        for i, q in enumerate(questions):
            user_answer = st.session_state.user_answers[i]
            correct_answer = q.get('correct_answer')
            score = q.get('score', 0)
            
            st.markdown(f"**سؤال {i+1}** ({QUESTION_TYPES.get(q['type'])} | الدرجة: {score}): **{q.get('text', 'لا يوجد نص')}**")

            if q['type'] in ['multiple_choice', 'true_false']:
                is_correct = user_answer == correct_answer
                
                if user_answer is not None:
                    if is_correct:
                        st.success(f"إجابتك: {user_answer} (صحيحة!)")
                        total_score += score
                    else:
                        st.error(f"إجابتك: {user_answer} (خاطئة)")
                        st.info(f"الإجابة الصحيحة: **{correct_answer}**")
                else:
                    st.warning("لم تجب على هذا السؤال.")
                    st.info(f"الإجابة الصحيحة: **{correct_answer}**")
                    
            elif q['type'] == 'essay':
                st.info(f"إجابتك المقالية:\n{user_answer or 'لم يتم الإجابة'}")
                st.markdown(f"**الإجابة النموذجية:** *{correct_answer}*")
                st.warning("درجة هذا السؤال المقالي لم تُحسب. يتم تقديرها لاحقاً.")

            st.markdown("---")

        st.markdown(f'<div class="final-score">النتيجة التقديرية (بدون المقالي): {total_score} من {max_score}</div>', unsafe_allow_html=True)
        
        if st.button("بدء اختبار جديد", key="quiz_restart"):
            st.session_state.quiz_in_progress = False
            st.session_state.show_results = False
            st.session_state.current_page = 'main'
            st.rerun()

    else:
        # --- واجهة حل الأسئلة أثناء الاختبار ---
        
        answered_count = sum(1 for ans in st.session_state.user_answers if ans is not None)
        st.info(f"عدد الأسئلة المجابة: {answered_count} / {len(questions)}")

        for i, q in enumerate(questions):
            q_type = q['type']
            
            # تحديد المفتاح لضمان عدم إعادة تعيين الإجابة
            key = f"quiz_q_{i}"
            
            st.subheader(f"سؤال {i+1} (الدرجة: {q.get('score', 0)}) | النوع: {QUESTION_TYPES.get(q_type)}")
            
            current_answer = st.session_state.user_answers[i]
            
            if q_type == 'multiple_choice':
                options = q.get('options', [])
                # إضافة خيار "عدم الإجابة" كخيار أول (None)
                options_with_none = ["لم أختر"] + options
                
                default_index = 0
                if current_answer in options:
                    default_index = options.index(current_answer) + 1 # +1 بسبب إضافة "لم أختر"
                
                selected_option = st.radio(
                    q.get('text'),
                    options_with_none,
                    index=default_index,
                    key=key
                )
                # تخزين الإجابة الفعلية أو None
                st.session_state.user_answers[i] = selected_option if selected_option != "لم أختر" else None
                
            elif q_type == 'true_false':
                options = ["صحيح", "خطأ"]
                default_index = options.index(current_answer) if current_answer in options else 0

                selected_option = st.radio(
                    q.get('text'),
                    options,
                    index=default_index,
                    key=key
                )
                st.session_state.user_answers[i] = selected_option

            elif q_type == 'essay':
                # نص مقالي
                current_value = current_answer if current_answer else ""
                essay_answer = st.text_area(
                    q.get('text'), 
                    value=current_value,
                    height=150,
                    key=key
                )
                # تخزين الإجابة فقط إذا لم تكن فارغة بعد الكتابة
                st.session_state.user_answers[i] = essay_answer if essay_answer.strip() else None

            st.markdown("***")

        if st.button("إنهاء الاختبار وعرض النتيجة", key="quiz_submit", type="primary"):
            st.session_state.show_results = True
            st.rerun()

# --- 🏠 وظيفة توجيه الصفحات الرئيسية ---

def main_page():
    """الصفحة الرئيسية لاختيار الوضع."""
    st.markdown("<h1 class='main-header'>نظام الاختبارات الديناميكي 📝</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>اختر وضع التشغيل:</h3>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("1️⃣ حل الاختبار", key="btn_quiz_mode", use_container_width=True):
            st.session_state.current_page = 'quiz'
            st.session_state.quiz_in_progress = False
            st.rerun()
            
    with col2:
        if st.button("2️⃣ الإعدادات (للمدير)", key="btn_settings_mode", use_container_width=True):
            st.session_state.current_page = 'login'
            st.rerun()
            
    st.markdown("<br><br><p style='text-align: center; color: #777;'>ملاحظة: البيانات محفوظة في ملف (quiz_data.pkl).</p>", unsafe_allow_html=True)

# --- 🚀 تشغيل التطبيق ---

def run_app():
    """المنطق الرئيسي لتشغيل التطبيق."""
    set_page_style() # تطبيق التنسيقات الفاخرة
    
    # توجيه الصفحات
    if st.session_state.current_page == 'main':
        main_page()
    elif st.session_state.current_page == 'login':
        login_page()
    elif st.session_state.current_page == 'settings':
        if st.session_state.logged_in:
            settings_page()
        else:
            st.session_state.current_page = 'login'
            st.rerun()
    elif st.session_state.current_page == 'quiz':
        quiz_page()

if __name__ == "__main__":
    run_app()
