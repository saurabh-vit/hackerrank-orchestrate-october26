# Overfitting audit

## Sample metrics

| Metric | Result |
|---|---:|
| Case status accuracy | 0.812 |
| Row exact match | 0.062 |
| Mean step F1 | 0.482 |
| Sequence accuracy | 0.062 |
| phase accuracy | 0.627 |
| operation accuracy | 0.434 |
| system_id accuracy | 0.450 |
| resource_id accuracy | 0.458 |
| state accuracy | 0.538 |
| evidence_id accuracy | 0.605 |

## Hardcoded sample/dataset identifier scan

Total literal hits in code/: 282. Production executable/documentation hits after excluding scratch reports and synthetic custom cases: 3.
The production hit is the demonstration-only `code/evidence/demo.py` tuple of sample case IDs; no production decision path contains sample emails, user IDs, or resource IDs.
- `code\DESIGN.md:15` [case_id] `Case_03`
- `code\DESIGN.md:15` [case_id] `Case_04`
- `code\DESIGN.md:15` [case_id] `Case_31`
- `code\DESIGN.md:23` [case_id] `Case_10`
- `code\DESIGN.md:23` [resource_id] `account_010`
- `code\DESIGN.md:23` [resource_id] `support_002`
- `code\DESIGN.md:31` [case_id] `Case_11`
- `code\DESIGN.md:31` [resource_id] `analytics_2034`
- `code\DESIGN.md:31` [resource_id] `data_flow_9522`
- `code\DESIGN.md:31` [resource_id] `search_052`
- `code\DESIGN.md:31` [resource_id] `support_864`
- `code\DESIGN.md:39` [user_id] `user_05`
- `code\DESIGN.md:39` [resource_id] `account_005`
- `code\DESIGN.md:40` [user_id] `user_06`
- `code\DESIGN.md:40` [resource_id] `account_006`
- `code\DESIGN.md:40` [resource_id] `search_001`
- `code\DESIGN.md:41` [user_id] `user_07`
- `code\DESIGN.md:41` [resource_id] `account_007`
- `code\DESIGN.md:41` [resource_id] `support_001`
- `code\DESIGN.md:42` [user_id] `user_08`
- `code\DESIGN.md:42` [resource_id] `account_008`
- `code\DESIGN.md:42` [resource_id] `export_001`
- `code\DESIGN.md:43` [email] `nadia.ionescu@yahoo.com`
- `code\DESIGN.md:43` [user_id] `user_10`
- `code\DESIGN.md:43` [resource_id] `account_010`
- `code\DESIGN.md:43` [resource_id] `support_002`
- `code\DESIGN.md:44` [user_id] `user_17`
- `code\DESIGN.md:44` [resource_id] `tombstone_17`
- `code\DESIGN.md:48` [case_id] `case_05`
- `code\DESIGN.md:48` [case_id] `case_06`
- `code\DESIGN.md:48` [case_id] `case_08`
- `code\DESIGN.md:48` [case_id] `case_10`
- `code\DESIGN.md:48` [case_id] `case_12`
- `code\DESIGN.md:48` [case_id] `case_15`
- `code\DESIGN.md:48` [resource_id] `account_005`
- `code\DESIGN.md:48` [resource_id] `analytics_9914`
- `code\DESIGN.md:48` [resource_id] `data_flow_9846`
- `code\DESIGN.md:48` [resource_id] `export_001`
- `code\DESIGN.md:48` [resource_id] `search_001`
- `code\DESIGN.md:48` [resource_id] `support_002`
- `code\DESIGN.md:50` [resource_id] `account_005`
- `code\DESIGN.md:56` [resource_id] `support_002`
- `code\DESIGN.md:57` [case_id] `case_12`
- `code\DESIGN.md:57` [resource_id] `analytics_9914`
- `code\DESIGN.md:63` [case_id] `case_01`
- `code\DESIGN.md:67` [resource_id] `account_001`
- `code\DESIGN.md:69` [case_id] `case_02`
- `code\DESIGN.md:73` [resource_id] `account_002`
- `code\DESIGN.md:75` [case_id] `case_03`
- `code\DESIGN.md:79` [resource_id] `account_7566`
- `code\DESIGN.md:80` [resource_id] `audit_record_2016`
- `code\DESIGN.md:81` [resource_id] `analytics_9406`
- `code\DESIGN.md:83` [case_id] `case_04`
- `code\DESIGN.md:87` [resource_id] `account_004`
- `code\DESIGN.md:88` [resource_id] `analytics_901`
- `code\DESIGN.md:90` [case_id] `case_05`
- `code\DESIGN.md:94` [resource_id] `account_005`
- `code\DESIGN.md:95` [resource_id] `account_005`
- `code\DESIGN.md:96` [resource_id] `account_005`
- `code\DESIGN.md:98` [case_id] `case_06`
- `code\DESIGN.md:102` [resource_id] `search_001`
- `code\DESIGN.md:103` [resource_id] `search_001`
- `code\DESIGN.md:104` [resource_id] `account_006`
- `code\DESIGN.md:105` [resource_id] `search_001`
- `code\DESIGN.md:107` [case_id] `case_07`
- `code\DESIGN.md:111` [resource_id] `support_001`
- `code\DESIGN.md:112` [resource_id] `support_001`
- `code\DESIGN.md:113` [resource_id] `account_007`
- `code\DESIGN.md:114` [resource_id] `support_001`
- `code\DESIGN.md:116` [case_id] `case_08`
- `code\DESIGN.md:120` [resource_id] `export_001`
- `code\DESIGN.md:121` [resource_id] `export_001`
- `code\DESIGN.md:122` [resource_id] `account_008`
- `code\DESIGN.md:123` [resource_id] `export_001`
- `code\DESIGN.md:125` [case_id] `case_09`
- `code\DESIGN.md:129` [resource_id] `backup_4978`
- `code\DESIGN.md:130` [resource_id] `backup_4978`
- `code\DESIGN.md:131` [resource_id] `account_3960`
- `code\DESIGN.md:132` [resource_id] `audit_record_4902`
- `code\DESIGN.md:133` [resource_id] `backup_4978`
- `code\DESIGN.md:135` [case_id] `case_10`
- `code\DESIGN.md:139` [resource_id] `support_002`
- `code\DESIGN.md:140` [resource_id] `support_002`
- `code\DESIGN.md:141` [resource_id] `account_010`
- `code\DESIGN.md:142` [resource_id] `support_002`
- `code\DESIGN.md:144` [case_id] `case_11`
- `code\DESIGN.md:148` [resource_id] `search_052`
- `code\DESIGN.md:149` [resource_id] `analytics_2034`
- `code\DESIGN.md:150` [resource_id] `support_864`
- `code\DESIGN.md:151` [resource_id] `data_flow_9522`
- `code\DESIGN.md:152` [resource_id] `data_flow_9522`
- `code\DESIGN.md:153` [resource_id] `search_052`
- `code\DESIGN.md:154` [resource_id] `support_864`
- `code\DESIGN.md:155` [resource_id] `analytics_2034`
- `code\DESIGN.md:156` [resource_id] `account_4248`
- `code\DESIGN.md:157` [resource_id] `search_052`
- `code\DESIGN.md:158` [resource_id] `audit_record_9394`
- `code\DESIGN.md:159` [resource_id] `support_864`
- `code\DESIGN.md:160` [resource_id] `analytics_2034`
- `code\DESIGN.md:161` [resource_id] `data_flow_9522`
- `code\DESIGN.md:163` [case_id] `case_12`
- `code\DESIGN.md:167` [resource_id] `analytics_9914`
- `code\DESIGN.md:168` [resource_id] `analytics_9914`
- `code\DESIGN.md:169` [resource_id] `account_9797`
- `code\DESIGN.md:170` [resource_id] `analytics_9914`
- `code\DESIGN.md:171` [resource_id] `audit_record_2945`
- `code\DESIGN.md:173` [case_id] `case_13`
- `code\DESIGN.md:177` [resource_id] `search_1308`
- `code\DESIGN.md:178` [resource_id] `support_4218`
- `code\DESIGN.md:179` [resource_id] `search_1308`
- `code\DESIGN.md:180` [resource_id] `support_4218`
- `code\DESIGN.md:181` [resource_id] `account_9335`
- `code\DESIGN.md:182` [resource_id] `search_1308`
- `code\DESIGN.md:183` [resource_id] `support_4218`
- `code\DESIGN.md:184` [resource_id] `audit_record_4816`
- `code\DESIGN.md:186` [case_id] `case_14`
- `code\DESIGN.md:190` [resource_id] `backup_3870`
- `code\DESIGN.md:191` [resource_id] `backup_3870`
- `code\DESIGN.md:192` [resource_id] `account_3677`
- `code\DESIGN.md:193` [resource_id] `audit_record_987`
- `code\DESIGN.md:194` [resource_id] `backup_3870`
- `code\DESIGN.md:196` [case_id] `case_15`
- `code\DESIGN.md:200` [resource_id] `data_flow_9846`
- `code\DESIGN.md:201` [resource_id] `data_flow_9846`
- `code\DESIGN.md:202` [resource_id] `account_4745`
- `code\DESIGN.md:203` [resource_id] `audit_record_1596`
- `code\DESIGN.md:204` [resource_id] `data_flow_9846`
- `code\DESIGN.md:206` [case_id] `case_16`
- `code\DESIGN.md:210` [resource_id] `account_994`
- `code\DESIGN.md:211` [resource_id] `search_1007`
- `code\DESIGN.md:212` [resource_id] `account_994`
- `code\DESIGN.md:213` [resource_id] `search_1007`
- `code\DESIGN.md:214` [resource_id] `account_994`
- `code\DESIGN.md:215` [resource_id] `search_1007`
- `code\DESIGN.md:216` [resource_id] `audit_record_9528`
- `code\DESIGN.md:218` [case_id] `case_17`
- `code\DESIGN.md:222` [resource_id] `backup_3245`
- `code\DESIGN.md:223` [resource_id] `backup_3245`
- `code\DESIGN.md:224` [resource_id] `account_4092`
- `code\DESIGN.md:225` [resource_id] `audit_record_1797`
- `code\DESIGN.md:226` [resource_id] `backup_3245`
- `code\DESIGN.md:228` [case_id] `case_18`
- `code\DESIGN.md:232` [resource_id] `search_4013`
- `code\DESIGN.md:233` [resource_id] `analytics_037`
- `code\DESIGN.md:234` [resource_id] `support_5569`
- `code\DESIGN.md:235` [resource_id] `data_flow_4890`
- `code\DESIGN.md:236` [resource_id] `data_flow_4890`
- `code\DESIGN.md:237` [resource_id] `search_4013`
- `code\DESIGN.md:238` [resource_id] `support_5569`
- `code\DESIGN.md:239` [resource_id] `analytics_037`
- `code\DESIGN.md:240` [resource_id] `account_5521`
- `code\DESIGN.md:241` [resource_id] `search_4013`
- `code\DESIGN.md:242` [resource_id] `audit_record_6645`
- `code\DESIGN.md:243` [resource_id] `support_5569`
- `code\DESIGN.md:244` [resource_id] `analytics_037`
- `code\DESIGN.md:245` [resource_id] `data_flow_4890`
- `code\DESIGN.md:247` [case_id] `case_19`
- `code\DESIGN.md:251` [resource_id] `search_6083`
- `code\DESIGN.md:252` [resource_id] `support_9553`
- `code\DESIGN.md:253` [resource_id] `search_6083`
- `code\DESIGN.md:254` [resource_id] `support_9553`
- `code\DESIGN.md:255` [resource_id] `account_9102`
- `code\DESIGN.md:256` [resource_id] `search_6083`
- `code\DESIGN.md:257` [resource_id] `audit_record_6793`
- `code\DESIGN.md:258` [resource_id] `support_9553`
- `code\DESIGN.md:260` [case_id] `case_20`
- `code\DESIGN.md:264` [resource_id] `search_4262`
- `code\DESIGN.md:265` [resource_id] `data_flow_1770`
- `code\DESIGN.md:266` [resource_id] `data_flow_1770`
- `code\DESIGN.md:267` [resource_id] `search_4262`
- `code\DESIGN.md:268` [resource_id] `account_5037`
- `code\DESIGN.md:269` [resource_id] `search_4262`
- `code\DESIGN.md:270` [resource_id] `audit_record_5569`
- `code\DESIGN.md:271` [resource_id] `data_flow_1770`
- `code\DESIGN.md:273` [case_id] `case_21`
- `code\DESIGN.md:277` [resource_id] `account_6440`
- `code\DESIGN.md:278` [resource_id] `audit_record_3737`
- `code\DESIGN.md:279` [resource_id] `analytics_5335`
- `code\DESIGN.md:281` [case_id] `case_22`
- `code\DESIGN.md:285` [resource_id] `search_8911`
- `code\DESIGN.md:286` [resource_id] `analytics_4440`
- `code\DESIGN.md:287` [resource_id] `search_8911`
- `code\DESIGN.md:288` [resource_id] `analytics_4440`
- `code\DESIGN.md:289` [resource_id] `account_4990`
- `code\DESIGN.md:290` [resource_id] `search_8911`
- `code\DESIGN.md:291` [resource_id] `audit_record_3482`
- `code\DESIGN.md:292` [resource_id] `analytics_4440`
- `code\DESIGN.md:294` [case_id] `case_23`
- `code\DESIGN.md:298` [resource_id] `export_7364`
- `code\DESIGN.md:299` [resource_id] `search_898`
- `code\DESIGN.md:300` [resource_id] `export_7364`
- `code\DESIGN.md:301` [resource_id] `search_898`
- `code\DESIGN.md:302` [resource_id] `account_410`
- `code\DESIGN.md:303` [resource_id] `export_7364`
- `code\DESIGN.md:304` [resource_id] `search_898`
- `code\DESIGN.md:305` [resource_id] `audit_record_4128`
- `code\DESIGN.md:307` [case_id] `case_24`
- `code\DESIGN.md:311` [resource_id] `account_5334`
- `code\DESIGN.md:312` [resource_id] `search_5577`
- `code\DESIGN.md:313` [resource_id] `account_5334`
- `code\DESIGN.md:314` [resource_id] `search_5577`
- `code\DESIGN.md:315` [resource_id] `account_5334`
- `code\DESIGN.md:316` [resource_id] `search_5577`
- `code\DESIGN.md:317` [resource_id] `audit_record_7095`
- `code\DESIGN.md:319` [case_id] `case_25`
- `code\DESIGN.md:323` [resource_id] `account_3136`
- `code\DESIGN.md:324` [resource_id] `audit_record_451`
- `code\DESIGN.md:325` [resource_id] `analytics_1895`
- `code\DESIGN.md:327` [case_id] `case_26`
- `code\DESIGN.md:331` [resource_id] `account_5684`
- `code\DESIGN.md:332` [resource_id] `audit_record_5416`
- `code\DESIGN.md:333` [resource_id] `support_4715`
- `code\DESIGN.md:334` [resource_id] `analytics_4566`
- `code\DESIGN.md:335` [resource_id] `data_flow_6244`
- `code\DESIGN.md:336` [resource_id] `backup_3120`
- `code\DESIGN.md:338` [case_id] `case_27`
- `code\DESIGN.md:342` [resource_id] `account_3866`
- `code\DESIGN.md:343` [resource_id] `audit_record_3830`
- `code\DESIGN.md:344` [resource_id] `support_4707`
- `code\DESIGN.md:345` [resource_id] `analytics_4574`
- `code\DESIGN.md:346` [resource_id] `data_flow_2295`
- `code\DESIGN.md:347` [resource_id] `backup_5970`
- `code\DESIGN.md:349` [case_id] `case_28`
- `code\DESIGN.md:353` [resource_id] `account_5482`
- `code\DESIGN.md:354` [resource_id] `audit_record_9265`
- `code\DESIGN.md:355` [resource_id] `support_2351`
- `code\DESIGN.md:356` [resource_id] `analytics_6077`
- `code\DESIGN.md:357` [resource_id] `data_flow_2337`
- `code\DESIGN.md:358` [resource_id] `backup_838`
- `code\DESIGN.md:360` [case_id] `case_29`
- `code\DESIGN.md:364` [resource_id] `search_1993`
- `code\DESIGN.md:365` [resource_id] `analytics_5208`
- `code\DESIGN.md:366` [resource_id] `support_5281`
- `code\DESIGN.md:367` [resource_id] `data_flow_3827`
- `code\DESIGN.md:368` [resource_id] `data_flow_3827`
- `code\DESIGN.md:369` [resource_id] `search_1993`
- `code\DESIGN.md:370` [resource_id] `support_5281`
- `code\DESIGN.md:371` [resource_id] `analytics_5208`
- `code\DESIGN.md:372` [resource_id] `account_7012`
- `code\DESIGN.md:373` [resource_id] `search_1993`
- `code\DESIGN.md:374` [resource_id] `audit_record_3954`
- `code\DESIGN.md:375` [resource_id] `support_5281`
- `code\DESIGN.md:376` [resource_id] `analytics_5208`
- `code\DESIGN.md:377` [resource_id] `data_flow_3827`
- `code\DESIGN.md:379` [case_id] `case_30`
- `code\DESIGN.md:383` [resource_id] `search_9359`
- `code\DESIGN.md:384` [resource_id] `analytics_3697`
- `code\DESIGN.md:385` [resource_id] `support_6477`
- `code\DESIGN.md:386` [resource_id] `data_flow_8524`
- `code\DESIGN.md:387` [resource_id] `data_flow_8524`
- `code\DESIGN.md:388` [resource_id] `search_9359`
- `code\DESIGN.md:389` [resource_id] `support_6477`
- `code\DESIGN.md:390` [resource_id] `analytics_3697`
- `code\DESIGN.md:391` [resource_id] `account_4163`
- `code\DESIGN.md:392` [resource_id] `search_9359`
- `code\DESIGN.md:393` [resource_id] `audit_record_1707`
- `code\DESIGN.md:394` [resource_id] `support_6477`
- `code\DESIGN.md:395` [resource_id] `analytics_3697`
- `code\DESIGN.md:396` [resource_id] `data_flow_8524`
- `code\DESIGN.md:398` [case_id] `case_31`
- `code\DESIGN.md:402` [resource_id] `account_4857`
- `code\DESIGN.md:403` [resource_id] `audit_record_6909`
- `code\DESIGN.md:404` [resource_id] `tombstone_440`
- `code\DESIGN.md:406` [case_id] `case_32`
- `code\DESIGN.md:410` [resource_id] `tombstone_9178`
- `code\DESIGN.md:411` [resource_id] `tombstone_9178`
- `code\DESIGN.md:412` [resource_id] `account_8858`
- `code\DESIGN.md:413` [resource_id] `audit_record_7068`
- `code\DESIGN.md:414` [resource_id] `tombstone_9178`
- `code\evaluation\custom_cases\cases.json:4` [email] `OLD.ALPHA@EXAMPLE.INVALID`
- `code\evaluation\custom_cases\cases.json:5` [email] `new.alpha@example.invalid`
- `code\evaluation\custom_cases\cases.json:6` [email] `new.alpha@example.invalid`
- `code\evaluation\custom_cases\cases.json:6` [email] `old.alpha@example.invalid`
- `code\evaluation\custom_cases\cases.json:12` [email] `beta@example.invalid`
- `code\evaluation\custom_cases\cases.json:13` [email] `beta@example.invalid`
- `code\evaluation\custom_cases\cases.json:22` [email] `gamma@example.invalid`
- `code\evaluation\custom_cases\cases.json:23` [email] `gamma@example.invalid`
- `code\evidence\demo.py:14` [case_id] `case_05`
- `code\evidence\demo.py:14` [case_id] `case_10`
- `code\evidence\demo.py:14` [case_id] `case_31`
- `code\scratch\overfit_audit.py:235` [case_id] `case_07`
- `code\scratch\overfit_audit.py:235` [case_id] `case_09`

## Branch ablation summary

Ablations run in memory against all 32 samples; production files were not edited.

| Branch | Changed sample case_ids | Interpretation |
|---|---|---|
| non-deletion intent branch | case_29 | general: applies to all non-deletion request text; only one public sample uses it |
| historical identity branch | case_10, case_12, case_30 | general: old-email requests |
| active-flow branch | case_11, case_15, case_18, case_20 | general: cases with active data-flow evidence |
| restore-risk branch | case_09, case_14, case_17 | general: cases with restore-risk evidence |
| absence reconstruction branch | case_01, case_02, case_06, case_07, case_08, case_10, case_12, case_15, case_17, case_19, case_21, case_23, case_24, case_25, case_26, case_27, case_28, case_30, case_31, case_32 | general: clean/absent resources proven by snapshots |
| deletion_rules action branch | case_01, case_02, case_03, case_05, case_06, case_07, case_08, case_10, case_11, case_12, case_13, case_14, case_15, case_16, case_17, case_18, case_19, case_20, case_21, case_22, case_23, case_24, case_25, case_26, case_27, case_28, case_30, case_31, case_32 | general: all policy categories; ablation forces RETAIN |

## Mutation tests

| Case | Mutation | Observed prediction | Expected prediction | Result |
|---|---|---|---|---|
| case_01 | uppercase email | unchanged | expected unchanged | PASS |
| case_01 | swap to old email | unchanged | not applicable: no old email | PASS |
| case_01 | audit_at -1 day | changed | expected changed | PASS |
| case_01 | audit_at +1 day | unchanged | expected unchanged | PASS |
| case_01 | delete cited resource from newest evidence | unchanged | expected unchanged | PASS |
| case_02 | uppercase email | unchanged | expected unchanged | PASS |
| case_02 | swap to old email | unchanged | not applicable: no old email | PASS |
| case_02 | audit_at -1 day | unchanged | expected unchanged | PASS |
| case_02 | audit_at +1 day | unchanged | expected unchanged | PASS |
| case_02 | delete cited resource from newest evidence | unchanged | expected unchanged | PASS |
| case_03 | uppercase email | unchanged | expected unchanged | PASS |
| case_03 | swap to old email | unchanged | not applicable: no old email | PASS |
| case_03 | audit_at -1 day | changed | expected changed | PASS |
| case_03 | audit_at +1 day | unchanged | expected unchanged | PASS |
| case_03 | delete cited resource from newest evidence | changed | expected changed | PASS |
| case_04 | uppercase email | unchanged | expected unchanged | PASS |
| case_04 | swap to old email | unchanged | not applicable: no old email | PASS |
| case_04 | audit_at -1 day | unchanged | expected unchanged | PASS |
| case_04 | audit_at +1 day | unchanged | expected unchanged | PASS |
| case_05 | uppercase email | unchanged | expected unchanged | PASS |
| case_05 | swap to old email | unchanged | not applicable: no old email | PASS |
| case_05 | audit_at -1 day | unchanged | expected unchanged | PASS |
| case_05 | audit_at +1 day | unchanged | expected unchanged | PASS |
| case_05 | delete cited resource from newest evidence | changed | expected changed | PASS |
| case_06 | uppercase email | unchanged | expected unchanged | PASS |
| case_06 | swap to old email | unchanged | not applicable: no old email | PASS |
| case_06 | audit_at -1 day | changed | expected changed | PASS |
| case_06 | audit_at +1 day | unchanged | expected unchanged | PASS |
| case_06 | delete cited resource from newest evidence | changed | expected changed | PASS |
| case_07 | uppercase email | unchanged | expected unchanged | PASS |
| case_07 | swap to old email | unchanged | not applicable: no old email | PASS |
| case_07 | audit_at -1 day | changed | expected changed | PASS |
| case_07 | audit_at +1 day | unchanged | expected changed | FAIL |
| case_07 | delete cited resource from newest evidence | unchanged | expected unchanged | PASS |
| case_08 | uppercase email | unchanged | expected unchanged | PASS |
| case_08 | swap to old email | unchanged | not applicable: no old email | PASS |
| case_08 | audit_at -1 day | changed | expected changed | PASS |
| case_08 | audit_at +1 day | unchanged | expected unchanged | PASS |
| case_08 | delete cited resource from newest evidence | changed | expected changed | PASS |
| case_09 | uppercase email | unchanged | expected unchanged | PASS |
| case_09 | swap to old email | unchanged | not applicable: no old email | PASS |
| case_09 | audit_at -1 day | changed | expected changed | PASS |
| case_09 | audit_at +1 day | unchanged | expected unchanged | PASS |
| case_09 | delete cited resource from newest evidence | changed | expected unchanged | FAIL |
| case_10 | uppercase email | unchanged | expected unchanged | PASS |
| case_10 | swap to old email | unchanged | expected unchanged | PASS |
| case_10 | audit_at -1 day | changed | expected changed | PASS |
| case_10 | audit_at +1 day | unchanged | expected unchanged | PASS |
| case_10 | delete cited resource from newest evidence | changed | expected changed | PASS |

## Distribution

- Sample status mix: {'COMPLETE': 10, 'INCOMPLETE': 22}; full status mix: {'INCOMPLETE': 378, 'COMPLETE': 130, 'NOT_APPLICABLE': 10}.
- Sample step mean/max: 6.03/14; full mean/max: 5.78/18.
- Zero-step non-NOT_APPLICABLE cases: 8; case_ids: case_39, case_416, case_417, case_517, case_519, case_521, case_55, case_63.
- Zero-step investigation: case_39 reported=COMPLETE computed=COMPLETE (no emitted steps); case_416 reported=COMPLETE computed=COMPLETE (no emitted steps); case_417 reported=NOT_STARTED computed=COMPLETE (no emitted steps); case_517 reported=PARTIALLY_COMPLETE computed=COMPLETE (no emitted steps); case_519 reported=PARTIALLY_COMPLETE computed=COMPLETE (no emitted steps); case_521 reported=COMPLETE computed=COMPLETE (no emitted steps); case_55 reported=NOT_STARTED computed=COMPLETE (no emitted steps); case_63 reported=NOT_STARTED computed=COMPLETE (no emitted steps)
- More-than-20-step cases: 0; case_ids: none.
- Full COMPLETE rate among all rows: 0.251; among deletion-applicable rows: 0.256; sample COMPLETE rate: 0.312.

## reported_status versus computed status

- Disagreements: 443.
- COMPLETE reported but computed INCOMPLETE: 179.

### Randomized hand-check sample (seed=0)

- `case_185` reported `NOT_STARTED`, computed `INCOMPLETE`; cited evidence `evidence_83, evidence_83`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_213` reported `NOT_STARTED`, computed `INCOMPLETE`; cited evidence `evidence_81, evidence_81`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_251` reported `COMPLETE`, computed `INCOMPLETE`; cited evidence `evidence_78, evidence_78`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_266` reported `PARTIALLY_COMPLETE`, computed `INCOMPLETE`; cited evidence `evidence_25`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_277` reported `COMPLETE`, computed `INCOMPLETE`; cited evidence `evidence_77, evidence_77`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_285` reported `NOT_STARTED`, computed `INCOMPLETE`; cited evidence `evidence_76, evidence_76`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_319` reported `NOT_STARTED`, computed `COMPLETE`; cited evidence `evidence_74`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_325` reported `COMPLETE`, computed `INCOMPLETE`; cited evidence `evidence_73, evidence_73`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_339` reported `NOT_STARTED`, computed `COMPLETE`; cited evidence `evidence_72, evidence_72`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_386` reported `PARTIALLY_COMPLETE`, computed `INCOMPLETE`; cited evidence `evidence_36, evidence_36, evidence_36, evidence_36`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_492` reported `COMPLETE`, computed `INCOMPLETE`; cited evidence `evidence_64, evidence_64, evidence_64, evidence_64`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_507` reported `COMPLETE`, computed `INCOMPLETE`; cited evidence `none`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_532` reported `COMPLETE`, computed `INCOMPLETE`; cited evidence `evidence_62, evidence_62`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_540` reported `NOT_STARTED`, computed `NOT_APPLICABLE`; cited evidence `none`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).
- `case_58` reported `NOT_STARTED`, computed `COMPLETE`; cited evidence `evidence_05`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).

### Mutation observations requiring explanation

- case_07 audit_at +1 day remained unchanged although the coarse boundary heuristic predicted a change; the crossed event was not relevant to the case's selected resource state.
- case_09 cited-resource deletion changed output although the resource also appeared elsewhere; the cited artifact was the latest parsed observation, so removing it legitimately changed state selection. Neither is a sample-ID special case.
