#!/usr/bin/env python3

from scripts.sbf import sbf
from scripts.stats import Stats


from cgitb import enable
enable()

from cgi import FieldStorage

print("Content-Type: text/html")
print()

form_data = FieldStorage()

mySBF = sbf(4, 'sha1', 3)
format_stats = Stats()

sbf_table = ""
sbf_check = ""
sbf_stats = ""

check_result = ""

if len(form_data) != 0:
    if form_data.getvalue("sbf_import"):
        mySBF.insert_from_file()
        sbf_result = mySBF.get_filter()
        for i in range(0, pow(2, 4)):
            sbf_table += "<td>{}</td>".format(str(sbf_result[i]))

        sbf_stats = format_stats.load_stats(mySBF.get_stats())

else:
    for i in range(0, pow(2, 4)):
        sbf_table += "<td>0</td>"
    sbf_stats = format_stats.load_initial_stats()

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

        <link rel="icon" type="image/x-icon" href="/images/favicon.ico">
        <link rel="stylesheet" type="text/css" href="/css/index.css" />
        <script type="text/javascript" src="js/index.js"></script>

        <title>FYP</title>
    </head>
    <body>
        <div class="navbar-fixed">
            <ul id="dropdown1" class="dropdown-content">
                <li><a href="dataset/cork.pdf">With Areas of Interest</a></li>
                <li class="divider"></li>
                <li><a href="dataset/cork-no-aoi.pdf">No Areas of Interest</a></li>
                <li class="divider"></li>
                <li><a href="dataset/cork.csv">Coordinates</a></li>
            </ul>
            <nav class="blue lighten-1">
                <div class="nav-wrapper">
                    <div class="container">
                        <a href="#" class="brand-logo">Spacial Bloom Filter</a>
                        <ul id="nav-mobile" class="right hide-on-med-and-down">
                            <li><a href="#">Link_1</a></li>
                            <li><a href="#">Link_2</a></li>
                            <li class="active"><a href="#">Link_3</a></li>
                            <!-- Dropdown Trigger -->
                            <li>
                                <a class="dropdown-button" href="#" data-activates="dropdown1">Cork Maps
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
                <div class="col s6 m6">
                    <div class="card horizontal">
                        <div class="card-stacked">
                            <div class="card-content">
                                <span class="card-title">The Data</span>
                                <div class="section">
                                    <p>
                                        The map of Cork has four marked Area's of Interest.<br>
                                        The coordinates of these areas are contained in a csv file.<br>
                                        Import these Area's of Interest and place them in the Spacial Bloom Filter.
                                    </p>
                                </div>
                                <div class="card-action">
                                    <form action="index.py" method="post">
                                        <input type="hidden" name="sbf_import" id="sbf_import" value="sbf_import">
                                        <!--input type="submit" value="Submit Query"-->
                                        <button class="btn waves-effect waves-light blue lighten-1 " type="submit">
                                            Import<i class="material-icons right">file_upload</i>
                                        </button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col s6 m6">
                    <div class="card horizontal">
                        <div class="card-stacked">
                            <div class="card-content">
                                <span class="card-title">The Details</span>
                                <div class="section">
                                    <p>
                                        The hash family selected is sha1.<br>
                                        The hash runs three times.
                                    </p>
                                </div>
                                <div class="card-action">
                                    <div  class="col s6 m6">
                                        <form action="index.py" method="post">
                                            <input type="hidden" name="sbf_details" id="sbf_details" value="sbf_details">
                                            <!--input type="submit" value="Submit Query"-->
                                            <button class="btn waves-effect waves-light blue lighten-1 disabled" type="submit">
                                                Submit<i class="material-icons right">send</i>
                                            </button>
                                        </form>
                                    </div>
                                    <div>
                                        <form action="index.py" method="post" class="col s6 m6">
                                            <input type="hidden" name="sbf_clear" id="sbf_clear" value="sbf_clear">
                                            <!--input type="submit" value="Submit Query"-->
                                            <button class="btn waves-effect waves-light blue lighten-1 disabled" type="submit">
                                                Clear Filter<i class="material-icons right">clear</i>
                                            </button>
                                        </form>
                                    </div>
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
                                <tr>
                                    <th>00</th>
                                    <th>01</th>
                                    <th>02</th>
                                    <th>03</th>
                                    <th>04</th>
                                    <th>05</th>
                                    <th>06</th>
                                    <th>07</th>
                                    <th>08</th>
                                    <th>09</th>
                                    <th>10</th>
                                    <th>11</th>
                                    <th>12</th>
                                    <th>13</th>
                                    <th>14</th>
                                    <th>15</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    {}
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col s12 m6">
                    <div class="card horizontal">
                        <div class="card-stacked">
                            <div class="card-content">
                                <span class="card-title">SBF Stats</span>
                                <div class="divider"></div>
                                <div class="section">
                                    <ul class="collection">
                                        {}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col s6 m6">
                    <div class="card horizontal">
                        <div class="card-stacked">
                            <div class="card-content">
                                <span class="card-title">Check SBF Values</span>
                                <div class="divider"></div>
                                <div class="section">
                                    Value:
                                    <div class="input-field inline">
                                        <input id="inputValue" type="text" class="validate">
                                        <label for="inputValue">Value</label>
                                    </div>
                                    <ul class="collection">
                                        <li id="result" class="collection-item">Result: {}</li>
                                    </ul>
                                </div>
                            </div>
                            <div class="card-action">
                                <button class="btn waves-effect waves-light blue lighten-1 disabled" type="button" name="import">
                                    Check<i class="material-icons right">check</i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </body>
</html>
""".format(sbf_table, sbf_stats, check_result))
