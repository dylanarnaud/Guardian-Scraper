# Libraries
import os
import sqlite3
from flask import Flask, request, jsonify
from datetime import date

class GuardianAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.__setup_routes()

    def __setup_routes(self):
        """Sets up the route endpoints."""
        self.app.add_url_rule('/items', 'get_items', self.__get_items, methods=['GET'])
        self.app.add_url_rule('/today', 'get_today', self.__get_today, methods=['GET'])
        self.app.add_url_rule('/last', 'get_last_article', self.__get_last_article, methods=['GET'])
        self.app.add_url_rule('/top-authors', 'get_top_authors', self.__get_top_authors, methods=['GET'])
        self.app.add_url_rule('/shutdown', 'shutdown', self.__shutdown, methods=['POST'])

    def __query_db(self, query, args=()):
        """Utility function to query the database and return rows."""
        with sqlite3.connect('guardian_database.db') as connection:
            cursor = connection.cursor()
            result = cursor.execute(query, args)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in result.fetchall()]

    def __get_items(self):
        """Endpoint to fetch a page of items."""
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        offset = (page - 1) * per_page

        query = """
            SELECT
                gua."ID Guardian"           AS GuardianID,
                gua."URL"                   AS Url,
                gua."Category"              AS Category,
                gua."Headline"              AS Headline,
                gua."Author"                AS Author,
                gua."Text"                  AS TextContent
            FROM DTM_V_D_GUARDIAN AS gua
            ORDER BY gua."ID Guardian" DESC
            LIMIT ? OFFSET ?
        """
        items = self.__query_db(query, (per_page, offset))
        return jsonify(current_page=page, per_page=per_page, items=items)

    def __get_today(self):
        """Endpoint to fetch today's items."""
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        offset = (page - 1) * per_page

        today_date = date.today().isoformat()

        query = """
            SELECT
                gua."ID Guardian"           AS GuardianID,
                gua."URL"                   AS Url,
                gua."Category"              AS Category,
                gua."Headline"              AS Headline,
                gua."Author"                AS Author,
                gua."Text"                  AS TextContent
            FROM DTM_V_FT_GUARDIAN AS ft
            INNER JOIN DTM_V_D_GUARDIAN AS gua
                ON ft."ID Guardian" = gua."ID Guardian"
            INNER JOIN DTM_V_D_DATE AS dat
                ON ft."ID Date" = dat."ID Date"
            WHERE dat."ID Date" = ?
            ORDER BY gua."ID Guardian" DESC
            LIMIT ? OFFSET ?
        """
        items = self.__query_db(query, (today_date, per_page, offset))
        return jsonify(current_page=page, per_page=per_page, items=items)

    def __get_last_article(self):
        """Endpoint to fetch the most recent article."""
        query = """
            SELECT
                gua."ID Guardian"               AS GuardianID
                ,gua."URL"                      AS Url
                ,gua."Category"                 AS Category
                ,gua."Headline"                 AS Headline
                ,gua."Author"                   AS Author
                ,gua."Text"                     AS TextContent
            FROM DTM_V_D_GUARDIAN AS gua
            WHERE gua."ID Guardian" = (SELECT MAX(g."ID Guardian") FROM DTM_V_D_GUARDIAN AS g)
        """
        items = self.__query_db(query)
        return jsonify(items[0] if items else {})

    def __get_top_authors(self):
        """Endpoint to fetch top authors by article count."""
        query = """
            SELECT
                gua."Author"                    AS Author
                ,COUNT(gua."Author")            AS ArticleCount
            FROM DTM_V_D_GUARDIAN AS gua
            GROUP BY gua."Author"
            ORDER BY COUNT(gua."Author") DESC, gua."Author" ASC
            LIMIT 5;
        """
        items = self.__query_db(query)
        return jsonify(items)

    def __shutdown(self):
        """Endpoint to safely shut down the server."""
        
        SECRET_KEY = "your_very_secret_key"  # Example secret key, use a more secure method in reality
        
        if self.app.debug and request.form.get('key') == SECRET_KEY:
            os._exit(0)
            
        return "Unauthorized", 401

    def run(self, debug=True, threaded=False, host='127.0.0.1'):
        """Run the Flask application."""
        self.app.run(debug=debug, threaded=threaded, host=host)

    
    def stop(self):
        """Stop the Flask application."""
        os._exit(0)

if __name__ == '__main__':
    api = GuardianAPI()
    api.run(debug=True)