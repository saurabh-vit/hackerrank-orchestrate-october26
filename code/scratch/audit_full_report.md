# Full output audit

| Check | Count | Offending case_ids | Evidence |
|---|---:|---|---|
| IDENTITY: unresolved or ambiguous requests | 0 | none | resolved=518; old-email-chain=101; case/whitespace variants=20 |
| IDENTITY: duplicated request email | 2 | case_33, case_52 | ingrid.dahl@outlook.com -> ['case_33', 'case_52'] -> users=['user_18'] |
| NOT_APPLICABLE: text classifier disagreement | 0 | none | text non-deletion=10; output NA=10; ambiguous=0 |
| NOT_APPLICABLE: CLASSIFY_REQUEST agreement | 0 | none | CLASSIFY_REQUEST events=10; linked cases=10; agreement=10/10 |
| EVIDENCE: unknown evidence IDs | 0 | none | no violations |
| EVIDENCE: future citations | 0 | none | no violations |
| EVIDENCE: citation not latest qualifying capture | 0 | none | no violations |
| EVIDENCE: cited file not grounded to user/resource | 125 | case_103, case_107, case_108, case_111, case_113, case_117, case_121, case_150, case_152, case_157, case_162, case_164, case_170, case_206, case_224, case_225, case_274, case_276, case_283, case_286, case_323, case_327, case_336, case_339, case_34, case_343, case_345, case_346, case_35, case_383, case_392, case_393, case_395, case_398, case_403, case_408, case_409, case_411, case_412, case_423, case_456, case_457, case_458, case_462, case_463, case_465, case_466, case_468, case_470, case_472, case_50, case_52, case_53, case_61, case_79, case_83 | no violations |
| EVIDENCE: INCOMPLETE remediation/verification not empty | 0 | none | no violations |
| EVIDENCE: COMPLETE step missing citation | 0 | none | no violations |
| POLICY: operation contradicts deletion rule | 11 | case_123, case_171, case_291, case_35, case_363, case_387, case_399, case_447, case_483, case_495, case_75 | retention checks=267; expired-at-audit=0 |
| POLICY: retention date expired at audit_at | 0 | none | Dates were compared with case audit_at, not wall-clock time |
| STRUCTURE: ordering violations | 0 | none | no violations |
| STRUCTURE: findings without remediation | 36 | case_147, case_151, case_175, case_191, case_213, case_231, case_233, case_235, case_277, case_279, case_292, case_297, case_315, case_324, case_326, case_331, case_335, case_35, case_351, case_390, case_41, case_435, case_44, case_463, case_464, case_471, case_480, case_51, case_531, case_532, case_64, case_77, case_81, case_82, case_87, case_99 | no violations |
| STRUCTURE: remediation without finding | 0 | none | no violations |
| STRUCTURE: remediation/verification orphan mismatch | 10 | case_123, case_171, case_291, case_363, case_387, case_399, case_447, case_483, case_495, case_75 | no violations |

## Identity explanations

- Total requests: 518; resolved: 518; unresolved/ambiguous: 0.
- Old-email-chain requests: 101; case/whitespace variants: 20.
- Duplicate request email handling: ingrid.dahl@outlook.com -> ['case_33', 'case_52'] -> users=['user_18'].

## Manual intent review

CLASSIFY_REQUEST events: 10; linked agreement: 10/10.

### Every NOT_APPLICABLE and linked deletion-sounding case

- case_533: The mobile number on my profile is out of date. Please replace it with the new one and leave the account active.
- case_534: Please stop the promotional emails. I still need the account and my order history, so I am not asking for deletion.
- case_535: I'd like to download my account information in a portable format. Please keep the account as it is.
- case_536: I can't access my profile and need help resetting the login. Do not close the account.
- case_537: My surname is misspelled on the account. Can you correct it without removing any of my records?
- case_538: Please remove me from marketing lists only. I still want receipts and service messages for this account.
- case_539: Can you tell me what personal information you hold about me? This is an information request, not a request to erase it.
- case_540: I need a copy of last year's invoices for my records. Please leave my profile and purchase history in place.
- case_541: Please change the email address used for this account. I want to continue using the service.
- case_542: Could you send me a copy of the information held on my account? I still use it, so please don't delete or change anything.

### Multilingual scan

- case_54 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_66 [INCOMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_69 [COMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_78 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_93 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_105 [INCOMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_108 [COMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_117 [COMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_132 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_144 [INCOMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_147 [INCOMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_156 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_171 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_183 [COMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_186 [INCOMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_195 [COMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_210 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_222 [INCOMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_225 [COMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_234 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_249 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_261 [INCOMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_264 [INCOMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_273 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_288 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_300 [INCOMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_303 [INCOMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_312 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_327 [COMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_339 [COMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_342 [INCOMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_351 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_366 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_378 [COMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_381 [INCOMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_390 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_405 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_417 [COMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_420 [INCOMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_429 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_444 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_456 [COMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_459 [INCOMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_468 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_483 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_495 [INCOMPLETE]: 이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요.
- case_498 [INCOMPLETE]: Solicito la eliminación permanente de la cuenta asociada a este correo. Revisen los identificadores actuales y anteriores según su política de privacidad. Por favor, confirmen el resultado cuando termine la revisión.
- case_507 [INCOMPLETE]: このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。
- case_522 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.
- case_546 [INCOMPLETE]: Solicito a exclusão permanente da conta associada a este e-mail. Verifiquem os identificadores atuais e anteriores conforme o processo de privacidade. Por favor, confirmem o resultado quando a análise terminar.

### Retention verification

Security/audit retention steps checked: 267; expired at audit_at: 0. Evidence text and ledger timestamps were compared to each case audit_at.

## Parser notes

Parsed evidence observations: 3246; evidence files: 94; audit rows: 306; activity rows: 4011.
Retention/legal-register evidence files inspected by name: 2; audit-ledger rows available for comparison: 306.
