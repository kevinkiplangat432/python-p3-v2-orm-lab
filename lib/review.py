from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )
    @property
    def year(self):
        return self._year
    @year.setter
    def year(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValueError("Year must be an integer.")
        if value < 2000:
            raise ValueError("Year must be >= 2000.")
        self._year = value


    @property
    def summary(self):
        return self._summary
    @summary.setter
    def summary(self, value):
        if not isinstance(value, str):
            raise TypeError("Summary must be a string.")
        if len(value) == 0:
            raise ValueError("Summary cannot be empty.")
        self._summary = value
    @property
    def employee_id(self):
        return self._employee_id
    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise TypeError("Employee ID must be an integer.")
        if value <= 0:
            raise ValueError("Employee ID must be a positive integer.")
        if Employee.find_by_id(value) is None:
            raise ValueError(f"No Employee exists with id {value}.")
        self._employee_id = value
    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """ 
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (year, summary, employee_id))
        CONN.commit()
        id = CURSOR.lastrowid
        new_review = cls(year, summary, employee_id, id)
        Review.all[id] = new_review
        return new_review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        review_id, year, summary, employee_id = row

        if review_id in cls.all:
            # Update the cached instance
            instance = cls.all[review_id]
            instance.year = year
            instance.summary = summary
            instance.employee_id = employee_id
            return instance

        # Otherwise create a new instance
        new_instance = cls(year, summary, employee_id, review_id)
        cls.all[review_id] = new_instance
        return new_instance

   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = """
            SELECT * FROM reviews WHERE id = ?
        """
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        else:
            return None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(
            sql, (self.year, self.summary, self.employee_id, self.id)
        )
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        sql = """
            DELETE FROM reviews WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = """
            SELECT * FROM reviews
        """
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        instances = []
        for row in rows:
            instance = cls.instance_from_db(row)
            instances.append(instance)
        return instances

