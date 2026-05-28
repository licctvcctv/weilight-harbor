import json
import datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from applications.extensions import db
from applications.models.journal_entry import JournalEntry
from applications.common.utils.files import save_multiple_uploads
from applications.view.journal import journal_bp


@journal_bp.route('/')
@login_required
def timeline():
    year = request.args.get('year', datetime.date.today().year, type=int)
    month = request.args.get('month', 0, type=int)

    query = JournalEntry.query.filter_by(user_id=current_user.id).filter(
        JournalEntry.delete_at.is_(None),
        db.extract('year', JournalEntry.entry_date) == year
    )
    if month and 1 <= month <= 12:
        query = query.filter(db.extract('month', JournalEntry.entry_date) == month)

    entries = query.order_by(JournalEntry.entry_date.desc()).all()

    years = db.session.query(
        db.extract('year', JournalEntry.entry_date).label('y')
    ).filter_by(user_id=current_user.id).filter(
        JournalEntry.delete_at.is_(None)
    ).group_by('y').all()
    available_years = sorted([int(y[0]) for y in years], reverse=True) if years else [datetime.date.today().year]

    # Get months with entries for the selected year
    months_with_entries = db.session.query(
        db.extract('month', JournalEntry.entry_date).label('m')
    ).filter_by(user_id=current_user.id).filter(
        JournalEntry.delete_at.is_(None),
        db.extract('year', JournalEntry.entry_date) == year
    ).group_by('m').all()
    available_months = sorted([int(m[0]) for m in months_with_entries]) if months_with_entries else []

    # Count all entries for the year (for annual film gate)
    total_year_count = JournalEntry.query.filter_by(user_id=current_user.id).filter(
        JournalEntry.delete_at.is_(None),
        db.extract('year', JournalEntry.entry_date) == year
    ).count()

    return render_template('public/journal/timeline.html',
                           entries=entries, current_year=year,
                           available_years=available_years, entry_count=total_year_count,
                           current_month=month, available_months=available_months)


@journal_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_entry():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        mood = request.form.get('mood', '')
        entry_date_str = request.form.get('entry_date', '')

        try:
            entry_date = datetime.datetime.strptime(entry_date_str, '%Y-%m-%d').date() if entry_date_str else datetime.date.today()
        except ValueError:
            entry_date = datetime.date.today()

        images = save_multiple_uploads(
            request.files.getlist('images'), 'journal', 'journal'
        )

        entry = JournalEntry(
            user_id=current_user.id, title=title, content=content,
            mood=mood, entry_date=entry_date,
            images=json.dumps(images) if images else None
        )
        db.session.add(entry)
        db.session.commit()
        flash('Journal entry saved!', 'success')
        return redirect(url_for('journal.timeline'))
    return render_template('public/journal/create_entry.html')


@journal_bp.route('/entry/<int:entry_id>')
@login_required
def view_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('journal.timeline'))
    return render_template('public/journal/view_entry.html', entry=entry)


@journal_bp.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('journal.timeline'))
    if request.method == 'POST':
        entry.title = request.form.get('title', '').strip()
        entry.content = request.form.get('content', '').strip()
        entry.mood = request.form.get('mood', '')
        db.session.commit()
        flash('Entry updated!', 'success')
        return redirect(url_for('journal.timeline'))
    return render_template('public/journal/edit_entry.html', entry=entry)


@journal_bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('journal.timeline'))
    entry.delete_at = datetime.datetime.now()
    db.session.commit()
    flash('Entry deleted.', 'success')
    return redirect(url_for('journal.timeline'))


@journal_bp.route('/annual-film')
@login_required
def annual_film():
    year = request.args.get('year', datetime.date.today().year, type=int)
    entries = JournalEntry.query.filter_by(user_id=current_user.id).filter(
        JournalEntry.delete_at.is_(None),
        db.extract('year', JournalEntry.entry_date) == year
    ).order_by(JournalEntry.entry_date.asc()).all()

    if len(entries) < 10:
        flash('Annual Film is available after you create at least 10 journal entries for the selected year.', 'warning')
        return redirect(url_for('journal.timeline', year=year))

    slides = []
    total_images = 0
    for e in entries:
        imgs = e.parsed_images
        total_images += len(imgs)
        slides.append({
            'date': e.entry_date.strftime('%B %d') if e.entry_date else '',
            'title': e.title or '',
            'excerpt': e.content or '',
            'mood': e.mood or '',
            'image': imgs[0] if imgs else None
        })

    if len(slides) > 12:
        step = len(slides) / 12
        slides = [slides[int(i * step)] for i in range(12)]

    stats = {
        'entry_count': len(entries),
        'month_count': len({e.entry_date.month for e in entries if e.entry_date}),
        'image_count': total_images,
        'year': year
    }
    return render_template('public/journal/annual_film.html',
                           slides=slides, stats=stats, year=year)
