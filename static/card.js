// Copyright 2016, Google, Inc.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

$(function(){
  // This is the host for the backend.
  // TODO: When running Firenotes locally, set to http://localhost:8081. Before
  // deploying the application to a live production environment, change to
  // https://backend-dot-<PROJECT_ID>.appspot.com as specified in the
  // backend's app.yaml file.
  // var backendHostUrl = 'https://backend-dot-fireproto-5c009.appspot.com';
  var backendHostUrl = 'https://synapcards.com';

  // Initialize Firebase
  var config = {
    apiKey: "AIzaSyCOrg4vnNpWniyNPB4_Gy2n0mv5t95DJJI",
    authDomain: "synapcards-178123.firebaseapp.com",
    databaseURL: "https://synapcards-178123.firebaseio.com",
    projectId: "synapcards-178123",
    storageBucket: "synapcards-178123.appspot.com",
    messagingSenderId: "266358714814"
  };

  // This is passed into the backend to authenticate the user.
  var userIdToken = null;
  var userId = null;
  var cardNum = null;
  // Signed in user data stored across functions.
  var cardData = null;

  // Firebase log-in
  function configureFirebaseLogin() {

    firebase.initializeApp(config);

    // [START onAuthStateChanged]
    firebase.auth().onAuthStateChanged(function(user) {
      // first pop gives userId:num, split again to find userId and cardNum
      cardId = window.location.href.split("/").pop();
      userId = cardId.split(":")[0];
      cardNum = cardId.split(":")[1];
      if (user) {
        user.getToken().then(function(idToken) {
          userIdToken = idToken;
          $('#signed-in-top').show();
          $('#signed-out-top').hide();
          $('#static-card-section').show();
          $('#dynamic-card-section').hide();
          $('#form-section').hide();
          $('#buttons-section').hide();
          $('#card-deleted-section').hide();
          $.ajax(backendHostUrl + '/cardajax', {
            headers: {'Authorization': 'Bearer ' + userIdToken},
            method: 'POST',
            data: JSON.stringify({
              'action': 'get',
              'user_id': userId,
              'card_num': cardNum,
            }),
            contentType : 'application/json'
          }).then(function(data){
            cardData = data;
            $('#signed-in-user-id-top').text(data.signed_in_user_id);
            link = backendHostUrl + '/user/' + data.signed_in_user_id;
            $('#self-profile-link-top').attr('href', link);
            console.log("user_id:" + userId);
            console.log("signed_in_user_id:" + data.signed_in_user_id);
            console.log("js v3");
            if (userId == data.signed_in_user_id) {
              console.log("matched signed in user");
              $('#static-card-section').hide();
              if (cardNum == 0) {
                showForm();
              } else {
                console.log("fill dynamic card");
                fillDynamicCard();
                $('#dynamic-card-section').show();
                console.log("showing buttons");
                $('#buttons-section').show();
              }
            }
          });
        });
      } else {
        // Signed out state.
        $('#signed-in-top').hide();
        $('#signed-out-top').show();
        $('#card-deleted-section').hide();
        $('#static-card-section').show();
        $('#dynamic-card-section').hide();
        $('#form-section').hide();
        $('#buttons-section').hide();
      }
    });
  }

  function showForm() {
    $('#static-card-section').hide();
    $('#dynamic-card-section').hide();
    $('#form-section').show();
    $('#buttons-section').hide();
  }

  function fillForm() {
    document.getElementById("title-textarea").value = cardData.title;
    document.getElementById("title-url-textarea").value = cardData.title_url;
    document.getElementById("summary-textarea").value = cardData.summary;
    document.getElementById("authors-textarea").value = cardData.authors;
    document.getElementById("source-textarea").value = cardData.source;
    document.getElementById("published-textarea").value = cardData.published;
    document.getElementById("tags-textarea").value = cardData.tags;
    console.log("Set dropdown selected to " + cardData.rating);
    var dropdown = document.getElementById("rating-dropdown");
    for (var i = 0; i < dropdown.options.length; i++) {
       if (dropdown.options[i].value == cardData.rating) {
           dropdown.options[i].selected = true;
       }
    }
    document.getElementById("detailed-notes-textarea").value = cardData.detailed_notes;
    $('#form-error-message').empty();
  }

  function clearForm() {
    document.getElementById("title-textarea").value = "";
    document.getElementById("title-url-textarea").value = "";
    document.getElementById("summary-textarea").value = "";
    document.getElementById("authors-textarea").value = "";
    document.getElementById("source-textarea").value = "";
    document.getElementById("published-textarea").value = "";
    document.getElementById("tags-textarea").value = "";
    document.getElementById("detailed-notes-textarea").value = "";
    $('#form-error-message').empty();
  }

  function fillDynamicCard() {
    $('#dynamic-card-id').text(cardData.card_id);
    $('#dynamic-title').text(cardData.title);
    $('#dynamic-title-html').html(cardData.title_html);
    $('#dynamic-summary').text(cardData.summary);
    $('#dynamic-authors').text(cardData.authors);
    $('#dynamic-source').text(cardData.source);
    $('#dynamic-published').text(cardData.published);
    $('#dynamic-tags').text(cardData.tags);
    $('#dynamic-rating').text(cardData.rating);
    $('#dynamic-max-rating').text(cardData.max_rating);
    $('#dynamic-detailed-notes').html(cardData.detailed_notes);
  }

  var signOutBtn =$('#sign-out');
  signOutBtn.click(function(event) {
    event.preventDefault();

    firebase.auth().signOut().then(function() {
      console.log("Sign out successful");
      userIdToken = null;
      cardData = null;
    }, function(error) {
      console.log(error);
    });
  });

  var deleteBtn =$('#delete-button');
  deleteBtn.click(function(event) {
    event.preventDefault();
    if (window.confirm('Delete this card?') == true){
      $.ajax(backendHostUrl + '/cardajax', {
        headers: {
          'Authorization': 'Bearer ' + userIdToken
        },
        method: 'POST',
        data: JSON.stringify({
          'action': 'delete',
          'user_id': userId,
          'card_num': cardNum,
        }),
        contentType : 'application/json'
      }).then(function(data){
        if ('error_message' in data) {
          console.log("delete error detected: " + data.error_message)
          window.alert(data.error_message);
        } else {
          console.log("delete success");
          cardData = null;
          $('#card-deleted-section').show();
          $('#static-card-section').hide();
          $('#dynamic-card-section').hide();
          $('#form-section').hide();
          $('#buttons-section').hide();
        }
      });
    }
  });

  var addBtn =$('#add-button');
  addBtn.click(function(event) {
    event.preventDefault();
    cardNum = '0';
    clearForm();
    showForm();
  });

  var editBtn =$('#edit-button');
  editBtn.click(function(event) {
    event.preventDefault();
    fillForm();
    showForm();
  });

  var cancelBtn =$('#cancel-button');
  cancelBtn.click(function(event) {
    event.preventDefault();
    $('#static-card-section').hide();
    $('#dynamic-card-section').show();
    $('#form-section').hide();
    // $('#error-user-id-container').empty();
    $('#buttons-section').show();
  });

  var saveBtn = $('#save-button');
  saveBtn.click(function(event) {
    console.log("Save button hit");
    event.preventDefault();

    var title = $('#title-textarea').val();
    var titleUrl = $('#title-url-textarea').val();
    var summary = $('#summary-textarea').val();
    var authors = $('#authors-textarea').val();
    var source = $('#source-textarea').val();
    var published = $('#published-textarea').val();
    var tags = $('#tags-textarea').val();
    var rating = $('#rating-dropdown').val();
    var detailedNotes = $('#detailed-notes-textarea').val();

    console.log("title: " + title);
    console.log("detailedNotes: " + detailedNotes);
    console.log("cardNum: " + cardNum);

    $.ajax(backendHostUrl + '/cardajax', {
      headers: {
        'Authorization': 'Bearer ' + userIdToken
      },
      method: 'POST',
      data: JSON.stringify({
        'action': 'save',
        'user_id': userId,
        'card_num': cardNum,
        'title': title,
        'title_url': titleUrl,
        'summary': summary,
        'authors': authors,
        'source': source,
        'published': published,
        'tags': tags,
        'rating': rating,
        'detailed_notes': detailedNotes,
      }),
      contentType : 'application/json'
    }).then(function(data){
      // Hide form container and display updated user info data.
      if ('error_message' in data) {
        console.log("error detected: " + data.error_message)
        $('#form-error-message').text(data.error_message);
      } else {
        console.log("post success (len good), go to dynamic data");
        cardData = data;
        // When saving a new card, update cardNum to value assigned by backend.
        cardNum = data.card_id.split(":")[1];
        console.log("returned cardNum: " + cardNum)
        fillDynamicCard();
        $('#static-card-section').hide();
        $('#dynamic-card-section').show();
        $('#form-section').hide();
        $('#buttons-section').show();
      }
    });
  });

  configureFirebaseLogin();
});
