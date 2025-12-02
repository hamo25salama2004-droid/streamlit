import streamlit as st
import time
import pickle
import os

# --- 🛠️ الثوابت والإعدادات الأولية ---

# ملف حفظ البيانات
DATA_FILE = 'quiz_data.pkl'
# اسم المستخدم وكلمة المرور للإعدادات
ADMIN_USERNAME = '2025'
ADMIN_PASSWORD = '2026'
# إجمالي وقت الاختبار بالثواني (يمكن تغييره في الإعدادات لاحقاً)
DEFAULT_QUIZ_TIME = 600  # 10 دقائق

# --- 💾 وظائف حفظ وتحميل البيانات ---

def load_data():
    """تحميل بيانات الأسئلة من الملف."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'rb') as f:
                data = pickle.load(f)
            # التأكد من وجود المفاتيح الضرورية
            if 'questions' not in data:
                data['questions'] = []
            if 'quiz_time' not in data:
                data['quiz_time'] = DEFAULT_QUIZ_TIME
            return data
        except Exception as e:
            st.error(f"خطأ في تحميل بيانات الاختبار: {e}. سيتم البدء ببيانات فارغة.")
            return {'questions': [], 'quiz_time': DEFAULT_QUIZ_TIME}
    return {'questions': [], 'quiz_time': DEFAULT_QUIZ_TIME}

def save_data(data):
    """حفظ بيانات الأسئلة في الملف."""
    try:
        with open(DATA_FILE, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        st.error(f"خطأ في حفظ بيانات الاختبار: {e}")


# تهيئة الجلسة وتحميل البيانات عند بدء تشغيل التطبيق
if 'data' not in st.session_state:
    st.session_state.data = load_data()
    st.session_state.logged_in = False
    st.session_state.current_page = 'main'
    st.session_state.quiz_in_progress = False

# --- 🔑 صفحة تسجيل الدخول (الإعدادات) ---

def login_page():
    """واجهة تسجيل الدخول للإعدادات."""
    st.header("🔑 تسجيل الدخول للإعدادات")

    if st.button("العودة للصفحة الرئيسية"):
        st.session_state.current_page = 'main'
        st.rerun()

    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submit_button = st.form_submit_button("تسجيل الدخول")

        if submit_button:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.current_page = 'settings'
                st.rerun() # لإعادة تحميل الصفحة وعرض الإعدادات
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

# --- ⚙️ صفحة الإعدادات (بعد تسجيل الدخول) ---

def settings_page():
    """واجهة إدارة الأسئلة وتعديل وقت الاختبار."""
    st.header("⚙️ إعدادات الاختبار")

    if st.button("العودة للصفحة الرئيسية"):
        st.session_state.current_page = 'main'
        st.rerun()
        return

    # 1. إدارة وقت الاختبار
    st.subheader("⏱️ إعداد وقت الاختبار الكلي")
    # التأكد من أن القيمة المحفوظة موجودة وصحيحة
    current_time_minutes = int(st.session_state.data.get('quiz_time', DEFAULT_QUIZ_TIME) / 60)
    
    new_quiz_time_min = st.number_input(
        "وقت الاختبار (بالدقائق)",
        min_value=1,
        max_value=120,
        value=current_time_minutes
    )
    if st.button("تحديث وقت الاختبار"):
        st.session_state.data['quiz_time'] = new_quiz_time_min * 60
        save_data(st.session_state.data)
        st.success(f"تم تحديث وقت الاختبار إلى {new_quiz_time_min} دقيقة.")

    st.markdown("---")

    # 2. إضافة سؤال جديد
    st.subheader("➕ إضافة سؤال جديد")
    with st.form("add_question_form", clear_on_submit=True):
        q_text = st.text_area("نص السؤال")
        q_option_a = st.text_input("الخيار أ")
        q_option_b = st.text_input("الخيار ب")
        q_option_c = st.text_input("الخيار ج")
        q_option_d = st.text_input("الخيار د")

        options_list = ['أ', 'ب', 'ج', 'د']
        correct_answer_label = st.selectbox(
            "الإجابة الصحيحة هي:",
            options_list
        )

        q_score = st.number_input("درجة السؤال:", min_value=1, value=5)

        add_button = st.form_submit_button("إضافة السؤال")

        if add_button:
            if q_text and q_option_a and q_option_b and q_option_c and q_option_d:
                options_map = {
                    'أ': q_option_a, 'ب': q_option_b,
                    'ج': q_option_c, 'د': q_option_d
                }

                new_question = {
                    'text': q_text,
                    'options': [q_option_a, q_option_b, q_option_c, q_option_d],
                    'correct_answer': options_map[correct_answer_label],
                    'score': q_score
                }
                st.session_state.data['questions'].append(new_question)
                save_data(st.session_state.data)
                st.success("تم إضافة السؤال بنجاح!")
            else:
                st.error("الرجاء ملء جميع حقول السؤال.")

    st.markdown("---")

    # 3. عرض ومراجعة الأسئلة
    questions = st.session_state.data.get('questions', [])
    st.subheader(f"📝 قائمة الأسئلة الحالية ({len(questions)} سؤال)")

    for i, q in enumerate(questions):
        st.write(f"**سؤال {i+1} (الدرجة: {q.get('score', 0)}):** {q.get('text', 'لا يوجد نص')}")
        st.write(f"الإجابة الصحيحة: **{q.get('correct_answer', 'غير محدد')}**")
        if st.button(f"حذف سؤال {i+1}", key=f"delete_{i}"):
            st.session_state.data['questions'].pop(i)
            save_data(st.session_state.data)
            st.success(f"تم حذف السؤال {i+1}.")
            st.rerun()

# --- 📝 صفحة حل الاختبار ---

def quiz_page():
    """واجهة عرض وحل الاختبار وحساب النتيجة."""
    questions = st.session_state.data.get('questions', [])
    total_time = st.session_state.data.get('quiz_time', DEFAULT_QUIZ_TIME)

    if not questions:
        st.warning("لا يوجد أسئلة حالياً. يرجى إضافة أسئلة من صفحة الإعدادات.")
        if st.button("العودة للصفحة الرئيسية"):
            st.session_state.current_page = 'main'
            st.rerun()
        return

    # بدء الاختبار ومنطق الوقت
    if not st.session_state.quiz_in_progress:
        st.session_state.quiz_in_progress = True
        st.session_state.start_time = time.time()
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.show_results = False

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, total_time - elapsed_time)

    # placeholder لعرض العداد
    time_placeholder = st.empty()

    if remaining_time > 0 and not st.session_state.show_results:
        # عرض الوقت المتبقي
        mins = int(remaining_time // 60)
        secs = int(remaining_time % 60)
        time_placeholder.markdown(f"**⏱️ الوقت المتبقي:** **{mins:02d}:{secs:02d}**")

        # تشغيل التحديث الذاتي (كل ثانية واحدة)
        # هذا يسمح للعداد بالعمل بانتظام
        time.sleep(1)
        st.rerun()

    elif remaining_time <= 0 and not st.session_state.show_results:
        # انتهاء الوقت
        time_placeholder.warning("🚫 انتهى الوقت!")
        st.session_state.show_results = True
        st.rerun() # لعرض صفحة النتيجة مباشرة

    st.markdown("---")

    if st.session_state.show_results:
        # --- عرض النتيجة بعد انتهاء الاختبار ---
        st.header("🎉 نتيجة الاختبار")
        total_score = 0
        max_score = sum(q.get('score', 0) for q in questions)

        for i, q in enumerate(questions):
            user_answer = st.session_state.user_answers[i]
            # التأكد من أن الإجابة الصحيحة موجودة
            correct_answer = q.get('correct_answer')
            score = q.get('score', 0)

            # في حالة انتهاء الوقت، قد تكون قائمة الإجابات أقصر
            if i >= len(st.session_state.user_answers):
                 st.warning(f"سؤال {i+1}: لم يتم الوصول إليه قبل انتهاء الوقت.")
                 continue

            is_correct = user_answer == correct_answer

            st.markdown(f"**سؤال {i+1}** ({score} نقطة): {q.get('text', 'لا يوجد نص')}")

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

            st.markdown("---")

        st.success(f"**النتيجة النهائية:** **{total_score}** من **{max_score}**")

        if st.button("بدء اختبار جديد"):
            st.session_state.quiz_in_progress = False
            st.session_state.show_results = False
            st.session_state.current_page = 'main'
            st.rerun()

    else:
        # --- واجهة حل الأسئلة أثناء الاختبار ---

        answered_count = sum(1 for ans in st.session_state.user_answers if ans is not None)
        st.info(f"عدد الأسئلة المجابة: {answered_count} / {len(questions)}")

        for i, q in enumerate(questions):
            st.subheader(f"سؤال {i+1} (الدرجة: {q.get('score', 0)})")

            options = q.get('options', [])
            if not options:
                st.error("خيارات السؤال غير متوفرة.")
                continue

            default_index = None
            if st.session_state.user_answers[i] in options:
                default_index = options.index(st.session_state.user_answers[i])

            # إضافة None كخيار أول (لعدم الإجابة)
            options_with_none = [None] + options

            selected_option = st.radio(
                q.get('text', 'نص السؤال غير متوفر'),
                options_with_none,
                index=default_index + 1 if default_index is not None else 0,
                key=f"q_{i}_radio"
            )

            # تحديث إجابة المستخدم
            st.session_state.user_answers[i] = selected_option

            st.markdown("***")

        if st.button("إنهاء الاختبار وعرض النتيجة"):
            st.session_state.show_results = True
            st.rerun()

# --- 🏠 وظيفة توجيه الصفحات الرئيسية ---

def main_page():
    """الصفحة الرئيسية لاختيار الوضع."""
    st.header("اختبار المبرمجين")
    # تم حذف السطر المسبب للخطأ هنا
    # st.image("", width=200)

    st.markdown("---")

    st.subheader("اختر وضع التشغيل:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("1️⃣ حل الاختبار", use_container_width=True):
            st.session_state.current_page = 'quiz'
            st.session_state.quiz_in_progress = False
            st.rerun()

    with col2:
        if st.button("2️⃣ الإعدادات (للمدير)", use_container_width=True):
            st.session_state.current_page = 'login'
            st.rerun()

# --- 🚀 تشغيل التطبيق ---

def run_app():
    """المنطق الرئيسي لتشغيل التطبيق."""
    st.set_page_config(page_title="نظام الاختبارات", layout="wide")

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
