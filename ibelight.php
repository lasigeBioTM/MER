<?php
echo "<pre>";
$old_path = getcwd();
chdir('/disk1/www/html/webtools/ibent/');
$output = shell_exec('./get_entities.sh '.$_GET['docid'].' '.$_GET['text'].' 2>&1');
echo $output;
echo "</pre>";
?>