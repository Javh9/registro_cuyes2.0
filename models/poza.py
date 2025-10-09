from extensions import db

class Poza(db.Model):
    __tablename__ = 'pozas'

    id = db.Column(db.Integer, primary_key=True)
    galpon_id = db.Column(db.Integer, db.ForeignKey('galpones.id'), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50))  # reproductores, engorde, destete, etc.
    capacidad = db.Column(db.Integer)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Poza {self.nombre} ({self.tipo})>'
