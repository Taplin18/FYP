#!/usr/bin/env python3

from cgitb import enable
enable()

print("Content-Type: text/html")
print()

print("""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">

            <!--Let browser know website is optimized for mobile-->
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>

            <!--Import jQuery-->
            <script type="text/javascript" src="https://code.jquery.com/jquery-3.3.1.min.js"></script>

            <!--Import Google Icon Font-->
            <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

            <!--Import materialize.css-->
            <link type="text/css" rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"  media="screen,projection"/>
            <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js"></script>

            <!--Import Angularjs-->
            <!--<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.6.4/angular.min.js"></script>-->


            <link rel="icon" type="image/x-icon" href="/images/favicon.ico">
            <link rel="stylesheet" type="text/css" href="/css/index.css" />
            <script type="text/javascript" src="js/index.js"></script>

            <title>FYP</title>
        </head>
        <body>
            <div class="navbar-fixed">
                <ul id="dropdown1" class="dropdown-content">
                    <li><a href="#">one</a></li>
                    <li><a href="#">two</a></li>
                    <li class="divider"></li>
                    <li><a href="#">three</a></li>
                </ul>
                <nav class="blue lighten-1">
                    <div class="nav-wrapper">
                        <div class="container">
                            <a href="#" class="brand-logo">SBF</a>
                            <ul id="nav-mobile" class="right hide-on-med-and-down">
                                <li><a href="#">Link_1</a></li>
                                <li><a href="#">Link_2</a></li>
                                <li class="active"><a href="#">Link_3</a></li>
                                <!-- Dropdown Trigger -->
                                <li>
                                    <a class="dropdown-button" href="#" data-activates="dropdown1">Dropdown
                                        <i class="material-icons right">arrow_drop_down</i>
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                </nav>
            </div>

            <div class="container">
                <div class="row">
                    <div class="col s12">
                        <div class="card horizontal">
                            <div class="card-stacked">
                                <div class="card-content">
                                    <span class="card-title">A Spatial Bloom Filter</span>
                                    <div class="divider"></div>
                                    <div class="section">
                                        <p>A spatial bloom filter is ...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col s12">
                        <div class="sbf">
                            <table id="myTable" class="centered"> <!--border=1 cellpadding=0 cellspacing=0-->
                                <thead>
                                    <tr id="labels"></tr>
                                </thead>
                                <tbody>
                                    <tr id="bits"></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!--<div class="row">-->
                    <!--<div class="col s12">-->
                        <!--<div class="card horizontal">-->
                            <!--<div class="card-stacked">-->
                                <!--<div class="card-content">-->
                                    <!--<span class="card-title">Insert values to SBF</span>-->
                                    <!--<div class="divider"></div>-->
                                    <!--<div class="section">-->
                                        <!--Input:-->
                                        <!--<div class="input-field inline">-->
                                            <!--<input id="inputValue" type="text" class="validate">-->
                                            <!--<label for="inputValue">Input</label>-->
                                        <!--</div>-->
                                        <!--<ul class="collection">-->
                                            <!--<li id="func1" class="collection-item">Function One:</li>-->
                                            <!--<li id="func2" class="collection-item">Function Two:</li>-->
                                            <!--<li class="collection-item">Values will be inserted into SBF.</li>-->
                                        <!--</ul>-->
                                    <!--</div>-->
                                <!--</div>-->
                                <!--<div class="card-action">-->
                                    <!--<button class="btn waves-effect waves-light" type="button" onclick="insertValue()">Insert-->
                                        <!--<i class="material-icons right">send</i>-->
                                    <!--</button>-->
                                <!--</div>-->
                            <!--</div>-->
                        <!--</div>-->
                    <!--</div>-->
                <!--</div>-->
            </div>

        </body>
    </html>
      """)
