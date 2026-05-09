import streamlit as st
import requests
import xml.etree.ElementTree as ET
import random

API_KEY = "6624DD55A9578E43F74B9B229168395E"

def check_word_exists(word):
    params = {'key': API_KEY, 'q': word, 'target': 1, 'method': 'exact', 'pos': 1}
    try:
        response = requests.get("https://opendict.korean.go.kr/api/search", params=params, verify=False)
        root = ET.fromstring(response.text)
        total = root.find('total').text
        return int(total) > 0
    except:
        return False

def find_next_word(last_char, used_words):
    dueum = {'라':'나', '락':'낙', '란':'난', '람':'남', '랑':'낭', '례':'예', '리':'이', '림':'임', '로':'노', '룡':'용', '류':'유', '륜':'윤'}
    start_chars = [last_char]
    if last_char in dueum:
        start_chars.append(dueum[last_char])
    for char in start_chars:
        params = {'key': API_KEY, 'q': char + '*', 'target': 1, 'method': 'wildcard', 'num': 50, 'pos': 1}
        try:
            response = requests.get("https://opendict.korean.go.kr/api/search", params=params, verify=False)
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            candidates = [i.find('word').text.replace('-', '').replace('^', '') for i in items]
            candidates = [w for w in candidates if len(w) >= 2 and w not in used_words]
            if candidates:
                return random.choice(candidates)
        except:
            continue
    return None

st.set_page_config(page_title="국어사전 끝말잇기", page_icon="🎮")
st.title("🎮 국어사전 끝말잇기 AI")

if 'used_words' not in st.session_state:
    st.session_state.used_words = []
if 'last_word' not in st.session_state:
    st.session_state.last_word = ""
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

with st.sidebar:
    if st.button("게임 다시 시작"):
        st.session_state.used_words = []
        st.session_state.last_word = ""
        st.session_state.game_over = False
        st.rerun()

for i, word in enumerate(st.session_state.used_words):
    if i % 2 == 0:
        st.chat_message("user").write(f"👤 나: {word}")
    else:
        st.chat_message("assistant").write(f"🤖 AI: {word}")

if not st.session_state.game_over:
    if st.session_state.last_word:
        prompt_text = f"'{st.session_state.last_word[-1]}'로 시작하는 단어 입력"
    else:
        prompt_text = "시작 단어를 입력하세요"
    user_input = st.chat_input(prompt_text)
    if user_input:
        if len(user_input) < 2:
            st.error("두 글자 이상 입력하세요.")
        elif st.session_state.last_word and user_input[0] != st.session_state.last_word[-1]:
            dueum_list = {'리':'이', '라':'나', '로':'노', '례':'예', '린':'인', '림':'임'}
            if not (st.session_state.last_word[-1] in dueum_list and user_input[0] == dueum_list[st.session_state.last_word[-1]]):
                st.error("끝말이 이어지지 않습니다.")
            else:
                pass
        elif user_input in st.session_state.used_words:
            st.error("이미 사용한 단어입니다.")
        else:
            with st.spinner("사전 확인 중..."):
                if check_word_exists(user_input):
                    st.session_state.used_words.append(user_input)
                    st.session_state.last_word = user_input
                    ai_word = find_next_word(user_input[-1], st.session_state.used_words)
                    if ai_word:
                        st.session_state.used_words.append(ai_word)
                        st.session_state.last_word = ai_word
                        st.rerun()
                    else:
                        st.balloons()
                        st.success("승리했습니다!")
                        st.session_state.game_over = True
                else:
                    st.error("사전에 없는 명사입니다.")
