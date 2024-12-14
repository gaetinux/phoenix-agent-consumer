import winrm
import base64
import sqlite3
import os

def main():
    # script to execute on server to get database of sessions
    ps_script = """
    $ProgressPreference = 'SilentlyContinue'
    Copy-Item 'C:\\ProgramData\\phoenix-agent\\sessions.db' -Destination 'C:\\ProgramData\\phoenix-agent\\sessions_temp.db'
    $db = [Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\\ProgramData\\phoenix-agent\\sessions_temp.db'))
    Remove-Item 'C:\\ProgramData\\phoenix-agent\\sessions_temp.db'
    return $db
    """

    # temp local session db
    temp_db = 'sessions.db'

    # connect to server to execute script
    s = winrm.Session('server', auth=('username', 'password'), transport='ntlm')
    r = s.run_ps(ps_script)

    if r.status_code == 0:
        # decode base64 et store db file locally
        encoded_content = r.std_out.strip()
        with open(temp_db, "wb") as f:
            f.write(base64.b64decode(encoded_content))
        print(f"Base SQLite téléchargée avec succès sous : {temp_db}")

        # connect to db file
        con = sqlite3.connect('sessions.db')
        cur = con.cursor()

        # execute sql query
        cur.execute("SELECT * FROM Sessions")

        # get all lines
        rows = cur.fetchall()
        
        # parse db data
        for row in rows:
            print(row)

        # close cursor and connection
        cur.close()
        con.close()

        # remove temp db file
        os.remove('sessions.db')
    else:
        print(f"Erreur lors de la récupération : {r.std_err}")

main()