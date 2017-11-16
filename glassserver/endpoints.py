from glassserver import db
from glassserver import models
from glassserver import media
from flask import request
from flask_restful import Resource
from flask_restful import fields, marshal_with
from datetime import timedelta

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


class ShowDetailed(Resource):
    @marshal_with(show_detailed_fields)
    def get(self, show_id):
        detailedShow = models.ShowDetailed.query.filter_by(id=show_id).first()
        return detailedShow


class Shows(Resource):
    @marshal_with(show_list_fields)
    def get(self):
        allShows = models.Show.query.order_by(models.Show.title).all()
        return {"shows": allShows}


class EpisodeDetailed(Resource):
    def get(self, episode_id):
        showViewState = request.args.get("viewstate", 0)
        userID = request.args.get("userid", 0)
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
        if showViewState:
            viewState = models.ViewState.query.filter_by(mediafile_id=file_id, user_id=userID).first()
            if viewState:
                ep["viewstate"] = {
                    "completed": viewState.completed,
                    "time": str(viewState.time)
                }
            else:
                ep["viewstate"] = {
                    "completed": False,
                    "time": str(timedelta(seconds=0))
                }
        return ep
