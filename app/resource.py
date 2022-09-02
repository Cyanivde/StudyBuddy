from flask import render_template
from app import app
from app.utils import _fetch_resource_df


@app.route('/resource/<resource_id>', methods=['GET', 'POST'])
def _resource(resource_id):
    resource_df = _fetch_resource_df(resource_id)
    resource = resource_df.iloc[0]
    resource_titles_df = resource_df[['course_id', 'course_name', 'rname', 'rname_part']]
    return render_template('resource.html', resource, resource_titles_df)
