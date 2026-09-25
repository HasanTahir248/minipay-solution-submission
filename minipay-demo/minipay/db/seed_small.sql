-- Small hand-crafted seed for fast local development / UI-API smoke testing.
-- For the ~50k-row dataset needed for INCIDENT-003 / performance work, use
-- db/generate_data.py instead (python generate_data.py > seed_large.sql).

INSERT INTO customers (customer_ref, name) VALUES
 ('CUST000001','Ayesha Khan'),
 ('CUST000002','Bilal Ahmed'),
 ('CUST000003','Sara Malik'),
 ('CUST000004','Omar Farooq'),
 ('CUST000005','Nida Hussain');

-- id 1
INSERT INTO transactions (transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code) VALUES
 ('TXN00000001', 1, 1500.00, 'SUCCESS', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '2 hours' + INTERVAL '5 seconds', NULL);
-- id 2
INSERT INTO transactions (transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code) VALUES
 ('TXN00000002', 2, 320.50, 'FAILED', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour' + INTERVAL '3 seconds', 'UPSTREAM_ERROR');
-- id 3
INSERT INTO transactions (transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code) VALUES
 ('TXN00000003', 3, 980.00, 'SUCCESS', NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes' + INTERVAL '2 seconds', NULL);
-- id 4: deliberately stuck in PROCESSING for >15 minutes (requirements/02-database.md query 3)
INSERT INTO transactions (transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code) VALUES
 ('TXN00000004', 4, 45000.00, 'PROCESSING', NOW() - INTERVAL '45 minutes', NULL, NULL);
-- id 5
INSERT INTO transactions (transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code) VALUES
 ('TXN00000005', 1, 2200.00, 'SUCCESS', NOW() - INTERVAL '10 minutes', NOW() - INTERVAL '10 minutes' + INTERVAL '4 seconds', NULL);
-- id 6
INSERT INTO transactions (transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code) VALUES
 ('TXN00000006', 5, 700.00, 'SUCCESS', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '3 hours' + INTERVAL '6 seconds', NULL);
-- id 7: deliberate DUPLICATE of TXN00000006's ref (see INCIDENT-001 / requirements/02 query 4)
INSERT INTO transactions (transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code) VALUES
 ('TXN00000006', 2, 150.00, 'SUCCESS', NOW() - INTERVAL '20 minutes', NOW() - INTERVAL '20 minutes' + INTERVAL '3 seconds', NULL);

INSERT INTO callbacks (transaction_id, attempt_no, http_status, callback_status, attempted_at) VALUES
 (1, 1, 200, 'SUCCESS', NOW() - INTERVAL '2 hours' + INTERVAL '10 seconds'),
 (2, 1, 502, 'FAILED',  NOW() - INTERVAL '1 hour' + INTERVAL '8 seconds'),
 (2, 2, 502, 'FAILED',  NOW() - INTERVAL '1 hour' + INTERVAL '13 seconds'),
 (3, 1, 200, 'SUCCESS', NOW() - INTERVAL '30 minutes' + INTERVAL '7 seconds'),
 (5, 1, 200, 'SUCCESS', NOW() - INTERVAL '10 minutes' + INTERVAL '9 seconds'),
 (6, 1, 200, 'SUCCESS', NOW() - INTERVAL '3 hours' + INTERVAL '11 seconds'),
 (7, 1, 200, 'SUCCESS', NOW() - INTERVAL '20 minutes' + INTERVAL '8 seconds');
