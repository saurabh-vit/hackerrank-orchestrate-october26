# Deletion-request intent classifier

Classify only the intent of the supplied request text.

Return JSON only, with exactly:

{"intent":"DELETION"|"NOT_APPLICABLE"|"AMBIGUOUS","confidence":"HIGH"|"MEDIUM"|"LOW","reason":"short reason"}

Use NOT_APPLICABLE when the person asks for an account/profile update, password/login help, marketing opt-out, access/information request, data copy/export, invoice copy, or explicitly says not to delete. Use DELETION only when the text requests account or personal-data deletion/erasure/removal. Preserve the meaning of multilingual text. Do not infer deletion from the surrounding email address or workflow status.
