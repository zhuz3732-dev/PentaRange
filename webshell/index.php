<?php
// Landing page for the uploads docroot. Deliberately lists the directory so a learner can see
// exactly what landed there, and shows whether .htaccess actually took effect.
$dir = __DIR__;
header('Content-Type: text/html; charset=utf-8');
?>
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>PentaRange · uploads</title>
<style>
body{background:#0d1117;color:#e6edf3;font:15px/1.6 ui-monospace,Consolas,monospace;padding:24px}
a{color:#f0883e} h1{font-size:18px} .ok{color:#3fb950} .dim{color:#8b949e}
code{background:#161b22;padding:1px 5px;border-radius:4px}
</style></head>
<body>
<h1>▚ PentaRange · uploads docroot (Apache + mod_php, port 8081)</h1>
<p class="dim">这个目录就是文件上传关卡的落地点。PHP 文件在这里<strong>会被执行</strong>。</p>
<p>mod_php: <span class="ok"><?php echo function_exists('apache_get_modules') || extension_loaded('apache2handler') ? 'enabled' : 'unknown'; ?></span>
 &nbsp;|&nbsp; PHP <?php echo PHP_VERSION; ?>
 &nbsp;|&nbsp; .htaccess 生效检测: <code><?php echo ini_get('allow_url_include') === '' ? 'n/a' : ''; ?><?php echo is_readable($dir.'/.htaccess') ? '.htaccess present' : 'no .htaccess'; ?></code></p>
<h2>目录内容</h2>
<ul>
<?php
$items = @scandir($dir) ?: [];
foreach ($items as $it) {
    if ($it === '.' || $it === '..') continue;
    $p = $dir . DIRECTORY_SEPARATOR . $it;
    $size = is_dir($p) ? '-' : number_format(filesize($p)) . ' B';
    printf('<li><a href="%s">%s</a> <span class="dim">(%s)</span></li>', rawurlencode($it), htmlspecialchars($it), $size);
}
?>
</ul>
<p class="dim">提示：黑名单只挡了 .php/.phtml 之类。想想还有没有别的扩展名或覆写手段。</p>
</body></html>