# encoding=utf-8

import os
import hashlib
import shutil
import os.path
import datetime
import logging
import tempfile

import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID, HSTORE, JSON

from . import app, db_engine, db_session, Base

from . import helpers

class FileSource(Base):
    __tablename__ = 'sources'

    id = sa.Column(sa.Integer, primary_key=True)
    dir = sa.Column(sa.Unicode(255), nullable=False)
    alias = sa.Column(sa.Unicode(255), nullable=False)


class ImageFile(Base):
    """ All information in this table is extracted from the image file itself,
        none if it is editable in any interface.
    """
    __tablename__ = 'files'

    id = sa.Column(sa.Integer, primary_key=True)
    path = sa.Column(sa.String(1000), nullable=False, unique=True)
    size = sa.Column(sa.Integer, nullable=False)
    hash = sa.Column(sa.String(128), nullable=False) # sha512 hexdigest
    width = sa.Column(sa.SmallInteger, nullable=False)
    height = sa.Column(sa.SmallInteger, nullable=False)
    ctime = sa.Column(sa.DateTime, nullable=False)
    format = sa.Column(sa.SmallInteger, nullable=False)

    # most important exif data
    date = sa.Column(sa.DateTime, nullable=True) # exif timestamp
    aperture = sa.Column(sa.Float, nullable=True)
    exposure = sa.Column(sa.Float, nullable=True)
    focal_length = sa.Column(sa.Float, nullable=True)
    focal_length_35 = sa.Column(sa.Float, nullable=True)
    iso = sa.Column(sa.Integer, nullable=True)
    make = sa.Column(sa.String(128), nullable=True)
    model = sa.Column(sa.String(128), nullable=True)
    orientation = sa.Column(sa.SmallInteger, nullable=True)

    # other exif stuff
    lens = sa.Column(sa.String(128), nullable=True)

    #exif = sa.Column(JSON, nullable=True)

    THUMB_SIZE = 256, 256
    LARGE_SIZE = 800, 800
    EXTENSIONS = {'jpg' : 1, 'jpeg' : 1, 'nef' : 2, 'cr2' : 3, 'crw' : 4, 'arw' : 5, 'srf' : 6, 'sr2' : 7}

    @classmethod
    def load(cls, file_path):
        size = os.path.getsize(file_path)
        ext = os.path.splitext(file_path)[1]
        with open(file_path) as f:
            m = hashlib.sha512()
            m.update(f.read())
            hash = m.hexdigest()
        stat = os.stat(file_path)

        _, large_path = tempfile.mkstemp()
        _, small_path = tempfile.mkstemp()

        try:
            info = helpers.process(file_path, [(cls.THUMB_SIZE, small_path), (cls.LARGE_SIZE, large_path)])

            obj = cls(
                path=file_path, 
                size=size, 
                hash=hash, 
                format=cls.EXTENSIONS[ext[1:].lower()],
                **info
                )

            shutil.move(large_path, obj.path_large)
            shutil.move(small_path, obj.path_thumb)

            return obj
        finally:
            if os.path.exists(large_path):
                os.remove(large_path)
            if os.path.exists(small_path):
                os.remove(small_path)


    @property
    def full_path(self):
        return self.path

    @property
    def path_thumb(self):
        actual_size = helpers.resize_dimensions((self.width, self.height), self.THUMB_SIZE) 
        return os.path.join(app.config['TEMP_DIR'], "%s_%d_%d.jpg" % (self.hash, actual_size[0], actual_size[1]))

    @property
    def path_large(self):
        actual_size = helpers.resize_dimensions((self.width, self.height), self.LARGE_SIZE) 
        return os.path.join(app.config['TEMP_DIR'], "%s_%d_%d.jpg" % (self.hash, actual_size[0], actual_size[1]))

    def dct(self):
        return {
            'id' : self.id,
            'size' : self.size,
            'width' : self.width,
            'height' : self.height,
            'ctime' : self.ctime,
            'filename' : os.path.basename(self.path), 
            'dirname' : os.path.dirname(self.path),
            'date' : self.date,
            'aperture': self.aperture,
            'exposure' : self.exposure,
            'focal_length' : self.focal_length,
            'focal_length_35' : self.focal_length_35,
            'iso' : self.iso,
            'orientation' : self.orientation,
            'make' : self.make,
            'model' : self.model,
            'lens' : self.lens
        }


class Photo(Base):
    ''' Photo() is an entity corresponding to a single photo.
        If several versions of a photo exists, for example due to post processing
        they are all linked to this single photo. '''
    __tablename__ = 'photos'
        
    id = sa.Column(sa.Integer, primary_key=True)
    shot= sa.Column(sa.Unicode(255), nullable=False)


class PhotoDerivative(Base):
    __tablename__ = 'derivatives'

    id = sa.Column(sa.Integer, primary_key=True)

    photo = relationship('Photo', backref=backref('derivatives'))
    photo_id = sa.Column(sa.Integer, sa.ForeignKey('photos.id'), nullable=False, primary_key=True)



class Person(Base):
    __tablename__ = "people"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255), nullable=False) # timestamp

