from flask import Flask, request, render_template
import sqlite3
import datetime
import logging

logging.basicConfig(filename="log.log", level=logging.INFO, filemode="w")
logger = logging.getLogger()

plain_v1_table = 'CREATE TABLE v1(organisation TEXT, application TEXT, current_version TEXT, last_version TEXT,' \
                 ' version_update_time TEXT, package_link TEXT, pin TEXT)'


def get_date_str():
    now = datetime.datetime.now()
    return now.strftime("%m/%d/%Y, %H:%M:%S")


def init_db():
    conn = sqlite3.connect('database.db')
    logger.info("connected to database successfully")
    # Check if table is complete
    try:
        conn.execute(plain_v1_table)
        logger.warning("database ' V1-Table ' created.")
        conn.close()

    except sqlite3.OperationalError:
        conn.close()
        logger.info("database check successfully")


# setup app
init_db()
app = Flask(__name__)


def api_query():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from v1")
    rows = cur.fetchall()
    return rows


def check_version(ext_ver, int_ver):
    if ext_ver == int_ver:
        result = ""


@app.route("/")
def index():
    logger.info(f"{request.access_route} -> Homepage")
    return render_template("home.html")


@app.route("/register")
def new_entry():
    logger.info(f"{request.access_route} -> Register")
    return render_template("register.html")


# api routes
@app.route("/api/v1/add_rec", methods=['POST'])
def addrec_v1():
    logger.warning(f"{request.access_route} -> Register Method")
    if request.method == 'POST':
        try:
            organisation = request.form['organisation']
            application = request.form['application']
            current_version = request.form['current_version']
            last_version = request.form['last_version']
            package_link = request.form['package_link']
            pin = request.form['pin']

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO v1 (organisation,"
                            "application,current_version,last_version,version_update_time,package_link, pin)"
                            "VALUES (?,?,?,?,?,?,?)", (organisation, application, current_version, last_version,
                                                       get_date_str(), package_link, pin))
            con.commit()
            msg = "Record successfully added"

        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            con.close()
            return render_template("result.html", msg=msg)


@app.route("/api/v1/<org>", methods=['GET'])
def api(org):
    logger.info(f"{request.access_route} -> {org}")
    con = sqlite3.connect("database.db")
    cursor = con.cursor()
    sql = f"SELECT * FROM v1 WHERE organisation ='{org}'"
    cursor.execute(sql)
    result = cursor.fetchall()

    if len(result) < 1:
        logger.warning("org not registerd")
        return render_template("result.html", msg=f"No entry for:'{org}'.")
    # at least 1 entry for org found
    else:
        application = request.args.get("app")
        user_version = request.args.get("version")

        # process data if arg provided
        if application is not None and user_version is not None:
            logger.warning(result)
            for x in result:
                if x[1] == application and x[2] == user_version:
                    return f"/{org}/{application}?match=true"

                if x[1] == application and x[3] == user_version:
                    return f"/{org}/{application}?match=behind&new={x[4]}&link={x[5]}"

                if x[1] == application and x[2] != user_version and x[3] != user_version:
                    return f"/{org}/{application}?match=far-behind&new={x[4]}&link={x[5]}"

                logger.warning(type(x))

        # do not handle request, args missing
        elif application is None or user_version is None:
            logger.error("api -> handle request -> args missing")
            return "denied"

        else:
            return "Something happened."


if __name__ == "__main__":
    app.run()
