-- -- User 데이터 삽입
-- INSERT INTO users (name, email, join_date, play_time) 
-- VALUES ('상쓰리', 'sangthree@naver.com', '2024-07-27 16:13:00', 20);

-- -- Voice 데이터 삽입
-- INSERT INTO voices (user_id, voice_name) 
-- VALUES 
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), '엄마'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), '아빠'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), '삼촌'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), '이모');

-- -- History 데이터 삽입
-- INSERT INTO histories (user_id, voice_id, situation, start_time, end_time, date, my_role, ai_role) 
-- VALUES 
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 1, '학교놀이', '16:13:00', '16:13:00', '2024-07-27', '학생', '선생님'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 2, '소꿉놀이', '16:13:00', '16:13:00', '2024-07-27', '남자친구', '여자친구'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 2, '소꿉놀이', '16:13:00', '16:13:00', '2024-07-27', '엄마', '아빠'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 3, '시장놀이', '16:13:00', '16:13:00', '2024-07-27', '할머니', '사장님'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 3, '가족놀이', '16:13:00', '16:13:00', '2024-07-27', '남편', '아내'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 4, '소꿉놀이', '16:13:00', '16:13:00', '2024-07-27', '동생', '형'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 1, '시장놀이', '16:13:00', '16:13:00', '2024-07-27', '엄마', '아들'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 1, '병원놀이', '16:13:00', '16:13:00', '2024-07-27', '환자', '의사'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 3, '학교놀이', '11:50:13', '11:50:13', '2024-08-01', '선생님', '학생'),
-- ((SELECT id FROM users WHERE email='sangthree@naver.com'), 4, '병원놀이', '02:13:56', '02:13:56', '2024-07-30', '환자', '의사');

-- INSERT INTO dialogs (history_id, user_id, speaker, message, message_time) VALUES
-- (1, 1, '학생', '선생님, 저 오늘 발표 준비했어요!', '2024-08-01 10:00:00'),
-- (1, 1, '선생님', '와, 정말 잘했구나! 그럼 어떤 주제로 발표를 준비했니?', '2024-08-01 10:00:10'),
-- (1, 1, '학생', '저는 공룡에 대해서 발표할 거예요. 공룡들이 어떻게 멸종했는지에 대해서요.', '2024-08-01 10:00:20'),
-- (1, 1, '선생님', '아, 공룡에 대해 공부했구나! 정말 흥미로운 주제네. 공룡들은 어떻게 멸종했는지 설명해 줄 수 있겠니?', '2024-08-01 10:00:30'),
-- (1, 1, '학생', '네! 공룡들은 6천 5백만 년 전에 큰 운석이 지구에 떨어져서 멸종했다고 해요. 그때 지구가 너무 많이 변해서 공룡들이 살 수 없게 됐대요.', '2024-08-01 10:00:40'),
-- (1, 1, '선생님', '아주 잘 설명했어! 그 당시 지구에서 어떤 변화들이 일어났을까?', '2024-08-01 10:00:50'),
-- (1, 1, '학생', '음, 하늘이 어두워지고, 기온이 많이 떨어졌다고 해요. 그래서 공룡들이 먹을 것도 없고, 살기도 어려웠을 거예요.', '2024-08-01 10:01:00'),
-- (1, 1, '선생님', '맞아, 하늘이 어두워지고 기온이 내려가면서 식물이 자라지 못했겠지. 그러면 공룡들이 먹을 것도 없어졌을 테니 정말 힘들었겠네.', '2024-08-01 10:01:10'),
-- (1, 1, '학생', '네, 그래서 공룡들이 점점 죽었대요. 저는 특히 티라노사우루스가 멸종된 게 슬퍼요. 티라노사우루스가 제일 좋아요.', '2024-08-01 10:01:20'),
-- (1, 1, '선생님', '티라노사우루스는 정말 멋진 공룡이지! 네가 티라노사우루스를 좋아하는 이유는 뭐니?', '2024-08-01 10:01:30'),
-- (1, 1, '학생', '티라노사우루스는 아주 크고 강하잖아요. 그리고 이빨도 엄청 날카롭고요! 무서우면서도 멋져요.', '2024-08-01 10:01:40'),
-- (1, 1, '선생님', '정말 멋진 이유네! 너처럼 티라노사우루스를 좋아하는 친구들도 많을 거야. 발표를 정말 잘 준비했구나. 자, 이제 발표를 친구들에게 해볼까?', '2024-08-01 10:01:50'),
-- (1, 1, '학생', '네, 선생님! 열심히 해볼게요!', '2024-08-01 10:02:00'),
-- (1, 1, '선생님', '좋아! 넌 할 수 있을 거야. 발표가 끝나고 나서 질문이 있으면 언제든지 선생님한테 물어보렴.', '2024-08-01 10:02:10'),
-- (1, 1, '학생', '감사합니다, 선생님!', '2024-08-01 10:02:20');


-- -- ResultReport 데이터 삽입
-- INSERT INTO result_reports (id, history_id, conversation_summary, child_questions, child_responses, interaction_summary, comprehensive_results)
-- VALUES 
-- (1, 10, 
-- '의사와 환자가 대화하는 상황입니다. 민규가 목이 아파서 의사 선생님에게 진료를 요청하고 있습니다. 의사 선생님은 민규의 열을 측정하고 약을 처방했습니다. 민규는 다음 번에 다시 진료받을 것을 기약하며 대화를 마무리 했습니다.', 
-- 12, 
-- 23, 
-- '의사가 대부분의 대화를 주도하면서 상황을 이끌어갔고, 환자 자신의 아픈 부분을 자세하게 설명하면서 활발한 상호작용이 이루어졌습니다.', 
-- '민규는 언어 발달 측면에서 매우 우수한 모습을 보이고 있습니다. 다양한 어휘를 활용하여 자신의 상태와 감정을 구체적으로 표현할 수 있으며, 대화의 주도권을 잡고 상호작용을 이끌어가는 능력이 있습니다. 감정 표현 능력도 충분히 발달되어 있으며, 이를 통해 자신의 정서 상태를 명확히 전달할 수 있습니다.'
-- );

-- -- Vocabulary 데이터 삽입 (언어 발달)
-- INSERT INTO vocabularies (id, result_report_id, development_type, total_word_count, basic_word_count, new_word_count)
-- VALUES 
-- (1, 1, true, 36, 17, 5);

-- -- Vocabulary 데이터 삽입 (정서 발달)
-- INSERT INTO vocabularies (id, result_report_id, development_type, total_word_count, basic_word_count, new_word_count)
-- VALUES 
-- (2, 1, false, 15, 31, 2);

-- -- UsedWord 데이터 삽입 (언어 발달 관련 새로운 단어)
-- INSERT INTO used_words (id, result_report_id, development_type, word)
-- VALUES 
-- (1, 1, true, '약'),
-- (2, 1, true, '아파요'),
-- (3, 1, true, '열나요'),
-- (4, 1, true, '감사합니다');

-- -- UsedWord 데이터 삽입 (정서 발달 관련 새로운 단어)
-- INSERT INTO used_words (id, result_report_id, development_type, word)
-- VALUES 
-- (5, 1, false, '감사합니다'),
-- (6, 1, false, '기뻐요'),
-- (7, 1, false, '행복해요');

-- -- UsedSentence 데이터 삽입 (언어 발달 관련 문장 구조)
-- INSERT INTO used_sentences (id, result_report_id, development_type, dialog_content, comment)
-- VALUES 
-- (1, 1, true, '얼굴이 화끈하고 머리가 지끈합니다', "'화끈하다', '지끈하다'라는 감각적인 어휘를 사용하여 신체적 감각이나 감정을 구체적으로 묘사했습니다."),
-- (2, 1, true, '목이 붓고 머리가 아파서 왔어요', "'목이 붓다', '머리가 아프다'라는 어휘를 사용하여 자신의 상태를 정확하게 묘사하고 있습니다. 단어 조합을 적절히 잘해서 활용하고 있습니다.");

-- -- UsedSentence 데이터 삽입 (정서 발달 관련 문장 구조)
-- INSERT INTO used_sentences (id, result_report_id, development_type, dialog_content, comment)
-- VALUES 
-- (3, 1, false, '하루종일 머리가 아파서 우울했어요', "'우울하다'라는 감정 표현을 직접적으로 활용하여 자신의 기분을 묘사했습니다."),
-- (4, 1, false, '하지만 맛있는 걸 먹어서 기분이 좋아졌어요', "'기분이 좋아지다'라는 감정 표현을 직접적으로 활용하여 자신의 기분을 묘사했습니다. 맛있는걸 먹고 난 후 긍정적인 감정 변화를 보였습니다.");
