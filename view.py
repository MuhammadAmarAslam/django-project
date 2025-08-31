from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Enrollment, Submission, Choice

# <HINT> Create a submit view to create an exam submission record for a course enrollment,
def submit(request, course_id):
    # Get the course and user enrollment
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = get_object_or_404(Enrollment, user=user, course=course)
    
    # Create a new submission object
    submission = Submission.objects.create(enrollment=enrollment)
    
    # Collect the selected choice IDs from the exam form
    selected_choice_ids = extract_answers(request)
    
    # Get the actual Choice objects from the database based on the IDs
    selected_choices = Choice.objects.filter(id__in=selected_choice_ids)
    
    # Add the choices to the submission using .set() with the list of objects
    submission.choices.set(selected_choices)
    
    # Redirect to the exam results page, passing the necessary arguments
    return HttpResponseRedirect(reverse('onlinecourse:exam_result', args=(course.id, submission.id,)))


# <HINT> An example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers


# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
def show_exam_result(request, course_id, submission_id):
    context = {}
    # Get the course and submission based on their IDs
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Get the selected choices from the submission
    selected_choices = submission.choices.all()
    
    # Calculate the total score
    total_score = 0
    # We need a set of all questions in the course to ensure we don't miss any
    # This loop assumes you get points for a question if a correct choice is selected.
    # A more robust logic would check if ALL correct choices for a question were selected.
    for choice in selected_choices:
        if choice.is_correct:
            total_score += choice.question.grade
    
    # Alternatively, a more advanced calculation (checking if all correct answers were selected):
    # total_score = 0
    # for question in course.question_set.all():
    #     if question.is_get_score(selected_choices):
    #         total_score += question.grade
    # (This requires a method `is_get_score` on the Question model)
    
    # Build the context for the template
    context['course'] = course
    context['submission'] = submission
    context['grade'] = total_score
    context['selected_choices'] = selected_choices # Fixed the variable name and assignment

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
