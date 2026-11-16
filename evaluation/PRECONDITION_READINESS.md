# Precondition readiness review

**This is infrastructure readiness, not application test results or a pass rate.**

Frozen suite SHA-256: `b9b1007098c297acb58158c21eb442a97deb49b835e893eda71c0dcab700ac37`.

75/100 cases currently have core actor setup supported; 25/100 need the explicit setup listed below. All 100 still require independent grading. Credentials configuration, model availability, paid budget approval and normal live NCBI availability are additional execution gates.

| Case | Actor setup | Explicit pending setup |
|---|---|---|
| T001 | Supported | — |
| T002 | Supported | — |
| T003 | Supported | — |
| T004 | Supported | — |
| T005 | Supported | — |
| T006 | Supported | — |
| T007 | Supported | — |
| T008 | Supported | — |
| T009 | Supported | — |
| T010 | Supported | — |
| T011 | Supported | — |
| T012 | Supported | — |
| T013 | Supported | — |
| T014 | Supported | — |
| T015 | Supported | — |
| T016 | Supported | — |
| T017 | Supported | — |
| T018 | Supported | — |
| T019 | Supported | — |
| T020 | Supported | — |
| T021 | Supported | — |
| T022 | Supported | — |
| T023 | Supported | — |
| T024 | Supported | — |
| T025 | Supported | — |
| T026 | Supported | — |
| T027 | Supported | — |
| T028 | Supported | — |
| T029 | Supported | — |
| T030 | Supported | — |
| T031 | Supported | — |
| T032 | Supported | — |
| T033 | Supported | — |
| T034 | Supported | — |
| T035 | Pending | registration_confirmation_request_fault |
| T036 | Supported | — |
| T037 | Pending | password_confirmation_request_fault |
| T038 | Supported | — |
| T039 | Supported | — |
| T040 | Pending | controlled_session_expiry_after_email_draft |
| T041 | Supported | — |
| T042 | Supported | — |
| T043 | Supported | — |
| T044 | Supported | — |
| T045 | Supported | — |
| T046 | Supported | — |
| T047 | Supported | — |
| T048 | Supported | — |
| T049 | Supported | — |
| T050 | Supported | — |
| T051 | Supported | — |
| T052 | Supported | — |
| T053 | Supported | — |
| T054 | Supported | — |
| T055 | Supported | — |
| T056 | Supported | — |
| T057 | Supported | — |
| T058 | Supported | — |
| T059 | Supported | — |
| T060 | Supported | — |
| T061 | Supported | — |
| T062 | Supported | — |
| T063 | Supported | — |
| T064 | Supported | — |
| T065 | Supported | — |
| T066 | Supported | — |
| T067 | Supported | — |
| T068 | Supported | — |
| T069 | Supported | — |
| T070 | Pending | bounded_three_second_upstream_delay |
| T071 | Supported | — |
| T072 | Supported | — |
| T073 | Supported | — |
| T074 | Pending | object_id_request_rewrite |
| T075 | Pending | csrf_and_origin_request_rewrite |
| T076 | Pending | controlled_cookie_collision_probe, password_hash_readonly_audit |
| T077 | Pending | controlled_session_expiry_with_research_page_open |
| T078 | Pending | return_parameter_name_from_preflight_navigation |
| T079 | Pending | credible_round1_legacy_migration_fixture |
| T080 | Supported | — |
| T081 | Supported | — |
| T082 | Pending | upstream_timeout_and_explicit_release |
| T083 | Pending | upstream_429_retry_after_sequence, current_ncbi_rate_limit_reference |
| T084 | Pending | upstream_503_and_explicit_release |
| T085 | Pending | partial_xml_record_fault, observable_cache_state |
| T086 | Pending | reversible_isolated_database_transaction_fault |
| T087 | Pending | configurable_60_second_cache_ttl, outbound_request_and_cache_auditor |
| T088 | Pending | synthetic_server_key_and_secret_auditor, upstream_503_fault |
| T089 | Pending | malformed_xml_fault_and_release |
| T090 | Pending | pagination_parameter_request_rewrite |
| T091 | Supported | — |
| T092 | Supported | — |
| T093 | Pending | controlled_session_expiry_multitab |
| T094 | Pending | controlled_session_expiry_after_private_draft |
| T095 | Pending | upstream_503_with_existing_private_library |
| T096 | Pending | credible_round1_legacy_migration_fixture |
| T097 | Supported | — |
| T098 | Pending | isolated_postgresql, controlled_app_restart_without_database_reset, postgres_readonly_state_auditor |
| T099 | Pending | api_contract_network_auditor |
| T100 | Supported | — |
