-- PentaRange seed data. Intentionally contains plaintext secrets: the whole point of the lab is
-- that this data leaks through the vulns. Never run this outside the isolated compose network.
CREATE DATABASE IF NOT EXISTS pentarange CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pentarange;

CREATE TABLE users (
  id       INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  password VARCHAR(128) NOT NULL,
  email    VARCHAR(128) NOT NULL,
  role     VARCHAR(16)  NOT NULL DEFAULT 'user',
  secret   VARCHAR(255) NOT NULL DEFAULT ''
);

CREATE TABLE notes (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title   VARCHAR(128) NOT NULL,
  body    TEXT
);

INSERT INTO users (username, password, email, role, secret) VALUES
  ('admin',   'PentaRange_admin_2026', 'admin@pentarange.local',  'admin', 'FLAG{sql1_union_based_extraction}'),
  ('alice',   'alice123',              'alice@pentarange.local',  'user',  'FLAG{stored_xss_cookie_theft}'),
  ('bob',     'bob123',                'bob@pentarange.local',    'user',  'FLAG{idor_read_other_mailbox}'),
  ('charlie', 'charlie123',            'c@pentarange.local',      'user',  'FLAG{ssrf_internal_metadata}');

INSERT INTO notes (user_id, title, body) VALUES
  (1, '部署说明', '生产环境 DSN: mysql://admin:PentaRange_admin_2026@db:3306/pentarange'),
  (2, '我的备忘', 'flag 在 users.secret 里，别告诉别人'),
  (3, 'todo',     '把 uploads 目录的执行权限关掉（暂时没关）');

CREATE TABLE flags (
  id       INT AUTO_INCREMENT PRIMARY KEY,
  level    VARCHAR(32) NOT NULL,
  tier     VARCHAR(8)  NOT NULL,
  flag     VARCHAR(128) NOT NULL
);

INSERT INTO flags (level, tier, flag) VALUES
  ('sqli',        'low',    'FLAG{sql1_union_based_extraction}'),
  ('sqli',        'medium', 'FLAG{sql2_blind_boolean_or_time}'),
  ('sqli',        'high',   'FLAG{sql3_waf_bypass_comment_split}'),
  ('xss',         'low',    'FLAG{xss1_reflected_no_encoding}'),
  ('xss',         'medium', 'FLAG{xss2_stored_cookie_theft}'),
  ('xss',         'high',   'FLAG{xss3_dom_sink_innerhtml}'),
  ('upload',      'low',    'FLAG{upload1_unrestricted_extension}'),
  ('upload',      'medium', 'FLAG{upload2_mime_whitelist_bypass}'),
  ('upload',      'high',   'FLAG{upload3_htaccess_override}'),
  ('ssrf',        'low',    'FLAG{ssrf1_internal_port_scan}'),
  ('ssrf',        'medium', 'FLAG{ssrf2_cloud_metadata_169254}'),
  ('ssrf',        'high',   'FLAG{ssrf3_dns_rebinding_bypass}'),
  ('deserialize', 'low',    'FLAG{deser1_pickle_rce}'),
  ('deserialize', 'medium', 'FLAG{deser2_yaml_gadget}'),
  ('deserialize', 'high',   'FLAG{deser3_php_object_injection}');
