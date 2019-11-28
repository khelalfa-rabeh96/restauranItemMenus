import os
import sys
from sqlachemy import Column, ForeignKey, Integer, String
from sqlachemy.ext.declarative import declarative_base
from sqlachemy.orm import relationship
from sqlachemy import create_engine

Base = declarative_base()

engine = create_engine('sqlite:///restaurantmenu.db?check_same_thread=False')
Base.metadata.create_all(engine)


