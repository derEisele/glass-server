from glassserver import db
from glassserver import models
from glassserver import media
from flask import request
from flask_restful import Resource
from flask_restful import fields, marshal_with

episode_fields = {
    "id":       fields.Integer,
    "season":   fields.Integer(attribute="season.season_number"),
    "episode":  fields.Integer(attribute="episode_number"),
    "title":    fields.String,
    "descr":    fields.String,
}

episode_detailed_fields = {
    "id":       fields.Integer,
    "season":   fields.Integer,
    "episode":  fields.Integer,
    "title":    fields.String,
    "descr":    fields.String

}

season_fields = {
    "id":       fields.Integer,
    "poster":   fields.String,
    "season":   fields.Integer(attribute="season_number"),
    "episodes": fields.List(fields.Nested(episode_fields))
}

show_fields = {
    "id":       fields.Integer,
    "title":    fields.String,
    "lang":     fields.String,
    "descr":    fields.String,
    "banner":   fields.String,
    "poster":   fields.String,
    "year":     fields.Integer,
    "imdb_id":  fields.String
}

show_detailed_fields = {
    "id":       fields.Integer,
    "title":    fields.String,
    "lang":     fields.String,
    "descr":    fields.String,
    "banner":   fields.String,
    "poster":   fields.String,
    "year":     fields.Integer,
    "imdb_id":  fields.String,
    "seasons":  fields.List(fields.Nested(season_fields))
}

show_list_fields = {
    "shows":    fields.List(fields.Nested(show_fields))
}


class Show(Resource):
    @marshal_with(show_fields)
    def get(self):
        shows = models.Show.query.all()
        return shows[0]

    @marshal_with(show_fields)
    def post(self):
        json_data = request.get_json()
        self.title = json_data["title"]
        self.year = json_data["year"]
        self.lang = json_data["lang"]
        self.descr = json_data["descr"]
        self.banner = json_data["banner"]
        show = models.Show(self.title, self.year, self.lang, self.descr, self.banner)
        db.session.add(show)
        db.session.commit()
        return show

class ShowDetailed(Resource):
    @marshal_with(show_detailed_fields)
    def get(self, show_id):
        detailedShow = models.ShowDetailed.query.filter_by(id=show_id).first()
        return detailedShow


class Shows(Resource):
    @marshal_with(show_list_fields)
    def get(self):
        allShows = models.Show.query.all()
        return {"shows": allShows}

class EpisodeDetailed(Resource):
    def get(self, episode_id):
        dbEpisode = models.Episode.query.filter_by(id=episode_id).first()
        dbShow = models.Show.query.filter_by(id=dbEpisode.season.show_id).first()
        #models.MediaFile.id
        file_id = dbEpisode.files[0].id
        ep = {"show":    dbShow.title,
              "show_id": dbShow.id,
              "title":   dbEpisode.title,
              "season":  dbEpisode.season.season_number,
              "episode": dbEpisode.episode_number,
              "urls":    media.generateUrls(file_id)}
        return ep
