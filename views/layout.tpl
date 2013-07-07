<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="HandheldFriendly" content="True">
        <meta name="MobileOptimized" content="320">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
        <title>{{title}}</title>
        <link rel="stylesheet" href="/static/css/ink.css">
        <link rel="stylesheet" href="/static/css/syntax.css">
        <link rel="stylesheet" href="/static/css/layout.css">
        <link rel="stylesheet" href="/static/css/debug.css">

        <!--[if IE 7 ]>
            <link rel="stylesheet" href="../css/ink-ie7.css" type="text/css" media="screen" title="no title" charset="utf-8">
        <![endif]-->
        
        <script src="/static/js/ink.js"></script>
%if defined('scripts'):
    %for script in scripts:    
        <script src="js/{{script}}"></script>
    %end
%end
    </head>
    <body>
        <div id="topbar">
            <!-- Desktop navigation -->
            <nav class="ink-navigation ink-grid hide-small hide-medium">
                <ul class="menu horizontal flat green">
                    <li class="title"><a href="/">Yaki</a></li>
                </ul>
            </nav>
            <!-- Mobile navigation -->
            <nav class="ink-navigation ink-grid hide-all show-medium show-small">
                <ul class="menu vertical flat green">
                    <li class="title"><a href="/space">Yaki</a>
                        <button class="toggle push-right" data-target="#topbar_menu" id="menu-toggle">
                            <span class="icon-reorder"></span>
                        </button>
                    </li>

                </ul>
                <ul class="menu vertical flat green hide-all" id="topbar_menu">
                   <li>
                   </li>
                </ul>
            </nav>
            <div class="border">
            </div>
        </div>
        </div>
        <!-- TODO: masthead -->

        <!-- TODO: sidebar -->
        <div id="main" class="ink-grid">
            <h1>{{title}}</h1>
            %include
        </div>
        <!-- TODO: footer -->
        <div class="screen-size-helper">
            <p class="title">Screen size:</h1>
            <ul class="unstyled">
                <li class="hide-medium hide-large show-small small">SMALL</li>
                <li class="hide-small show-medium hide-large medium">MEDIUM</li>
                <li class="hide-small hide-medium show-large large">LARGE</li>
            </ul>
        </div>
    </body>
</html>
