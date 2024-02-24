
import os

from flask import Flask, current_app, jsonify, render_template, request, flash, redirect, session, url_for
from werkzeug.utils import secure_filename


from database import db
from main.forms import ApplicationForm, JobPostForm
from main.models import JobApplication, JobPost
from users.routes import manager_required
from google_drive import upload_to_drive

from flask import Blueprint



main = Blueprint('main', __name__)





@main.route('/')
def index():
    # Query the database to get the most recent 3 job openings
    recent_job_openings = JobPost.query.order_by(JobPost.created_at.desc()).limit(3).all()
    google_maps_api_key = current_app.config['GOOGLE_MAPS_API_KEY']

    image_folder = 'indeximages'  # Folder inside 'static'
    image_directory = os.path.join(current_app.static_folder, image_folder)
    # List all jpg and jpeg files
    images = [os.path.join(image_folder, file) for file in os.listdir(image_directory) if file.lower().endswith(('.jpg', '.jpeg'))]
    return render_template('index.html', recent_job_openings=recent_job_openings, google_maps_api_key=google_maps_api_key, images=images)


@main.route('/images')
def images():
    image_directory = os.path.join('static', 'indeximages')
    images = [img for img in os.listdir(image_directory) if img.endswith(('.png', '.jpg', '.jpeg'))]
    return jsonify(images=images)

@main.route('/main/promotion_images')
def promotion_images():
    image_directory = os.path.join('static', 'indexpromotions')
    images = [img for img in os.listdir(image_directory) if img.endswith(('.png', '.jpg', '.jpeg'))]
    return jsonify(images=images)




@main.route('/store_locations')
def store_locations():
    return render_template('store_locations.html')


@main.route('/job_post', methods=['GET', 'POST'])
@manager_required
def job_post():
    form = JobPostForm()
    if form.validate_on_submit():
        job_post = JobPost(
            title=form.title.data,
            company=form.company.data,
            location=form.location.data,
            job_type=form.job_type.data,
            description=form.description.data,
            qualifications=form.qualifications.data
        )
        db.session.add(job_post)
        db.session.commit()
        return redirect(url_for('main.job_post'))
       
    job_posts = JobPost.query.all()
    return render_template('job_post.html', form=form, job_posts=job_posts)


@main.route('/delete_job/<int:id>', methods=['POST'])
def delete_job(id):
    # Retrieve the job opening from the database using the provided ID
    job_post = JobPost.query.get(id)

    if job_post is None:
        # Handle the case where the job opening with the given ID doesn't exist
        flash('Job opening not found.', 'error')
        return redirect(url_for('main.job_post'))

    # Delete the job opening from the database
    db.session.delete(job_post)
    db.session.commit()

    flash('Job opening deleted successfully.', 'success')
    return redirect(url_for('main.job_post'))


# Create a route to render the jobs.html page
@main.route('/jobs')
def job_listings():
    # Query the database to retrieve all job openings
    job_openings = JobPost.query.all()
    
    # Render the jobs.html template and pass the job_openings data
    return render_template('jobs.html', job_openings=job_openings)



@main.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    # Retrieve the specific job post using its ID
    job_post = JobPost.query.get(job_id)

    # Check if the job post exists
    if job_post is None:
        flash('Job opening not found.', 'error')
        return redirect(url_for('main.job_listings'))

    # Initialize the application form
    form = ApplicationForm()

    # Handle form submission
    if form.validate_on_submit():
        # Extract data from the form
        full_name = form.full_name.data
        email = form.email.data
        phone_number = form.phone_number.data
        education = form.education.data
        experience = form.experience.data
        reference = form.reference.data

        # Process the resume file upload
        resume_file = form.resume.data
        if resume_file:
            # Secure the filename
            filename = secure_filename(resume_file.filename)

            # Google Drive folder ID where resumes will be uploaded
            folder_id = '1HV4J1cBYD7Lo4sy2y4wjll4zM_xo1cko'

            try:
                # Upload the file directly from memory to Google Drive and get the file ID
                file_id = upload_to_drive(resume_file.stream, filename, folder_id)
            except Exception as e:
                # Handle exceptions during file upload
                flash(f'An error occurred while uploading the file to Google Drive: {e}', 'error')
                return render_template('jobapplication.html', job_post=job_post, form=form)

            # Create a new job application record with the Google Drive file ID
            job_application = JobApplication(
                job_post_id=job_id,
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                education=education,
                experience=experience,
                reference=reference,
                resume_filename=file_id  # Storing Google Drive file ID
            )
        else:
            # Create a new job application record without a resume file
            job_application = JobApplication(
                job_post_id=job_id,
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                education=education,
                experience=experience,
                reference=reference
            )

        # Add the new job application to the database
        db.session.add(job_application)
        db.session.commit()

        # Notify the user of successful submission
        flash('Job application submitted successfully!', 'success')
        return redirect(url_for('main.job_listings'))

    # Render the job application form template
    return render_template('jobapplication.html', job_post=job_post, form=form)


@main.route('/trainingvideos')
def trainingvideos():
    return render_template('trainingvideos.html')
