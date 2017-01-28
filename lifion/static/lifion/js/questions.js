/**
 * Created by doodla on 1/27/2017.
 */

$(document).ready(function () {


    var MAX_OPTIONS = 4;
    var optionIndex = 0;

    var $form = $("#add_question_form");

    $form
        .on('click', '.addButton', function () {
            optionIndex++;
            var $template = $('#optionTemplate'),
                $clone = $template
                    .clone()
                    .removeClass('hide')
                    .removeAttr('id')
                    .attr('data-index', optionIndex)
                    .insertBefore($template);

            $clone
                .find('[type="text"]').attr('name', 'text').prop('required', true).end()
                .find('[type="number"]').attr('name', 'points').prop('required', true).end();


            if (optionIndex == (MAX_OPTIONS - 1))
                $('#add_question_form').find('.addButton').attr('disabled', 'disabled');
        })
        .on('click', '.removeButton', function () {
            var $row = $(this).parents('.form-group');


            if (optionIndex < MAX_OPTIONS) {
                $('#add_question_form').find('.addButton').removeAttr('disabled');
            }

            // Remove element containing the fields
            $row.remove();
            optionIndex--;
        });


    function insertQuestion() {

        var questionHTML = "";
        questionHTML += "<div class=\"panel panel-default\">";
        questionHTML += "	<div class=\"panel-body\">";
        questionHTML += "		<div class=\"question\">";
        questionHTML += "			<div class=\"well\">";
        questionHTML += "				%QTEXT%";
        questionHTML += "			<\/div>";
        questionHTML += "			<div class=\"question-options\">";
        questionHTML += "				<div class=\"form-group\">";
        questionHTML += "					<div class=\"col-xs-12\">%RADIOS%<\/div>";
        questionHTML += "				<\/div>";
        questionHTML += "			<\/div>";
        questionHTML += "		<\/div>";
        questionHTML += "	<\/div>";
        questionHTML += "<\/div>";

        var radio = "";
        radio += "<div class=\"radio\">";
        radio += "	<label><input disabled type=\"radio\">%RTEXT% [%RVALUE%]<\/label>";
        radio += "<\/div>";


        var texts = [];

        $('input[name="text"]').each(function () {
            texts.push($(this).val());
        });

        var vals = [];

        $('input[name="points"]').each(function () {
            vals.push($(this).val());
        });

        var radioHtml = "";

        for (var i = 0; i < texts.length; i++) {
            (function () {
                var replacements = {
                    '%RTEXT%': texts[i],
                    '%RVALUE%': vals[i]
                };

                radioHtml += radio.replace(/%\w+%/g, function (all) {
                    return replacements[all] || all;
                });
            })();
        }


        replacements = {
            '%RADIOS%': radioHtml,
            '%QTEXT%': $('input[name="q_text"]').val()
        };

        questionHTML = questionHTML.replace(/%\w+%/g, function (all) {
            return replacements[all] || all;
        });

        var $questions = $("#questions");

        $questions.append(questionHTML)

    }

    $form.submit(function () {

        console.log($form.attr('action'));
        $.post($form.attr('action'), $form.serialize(), function (json) {

            var q_id = json['q_id'];
            //Get question id

            //Get current list of questions
            var $questionArr = $("#questionArr");

            var arr = [];
            if ($questionArr.val() != '') {
                arr = $questionArr.val().split(',');
            }
            arr.push(q_id);

            $questionArr.val(arr);

            insertQuestion();

            $("#create_survey").show();

        }, 'json');

        $("#add_question_modal").modal('hide');
        return false;

    });


});