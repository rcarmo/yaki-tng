<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>{{title}}</title>
        <link rel="stylesheet" href="/static/css/ink.css">
        <script src="/static/js/ink.js"></script>
%if defined('scripts'):
    %for script in scripts:    
        <script src="js/{{script}}"></script>
    %end
%end
    </head>
    <body>
        <!-- TODO: masthead -->
        <!-- TODO: sidebar -->
        <div id="main" class="ink-grid">
            %include
        </div>
        <!-- TODO: footer -->
    </body>
</html>
