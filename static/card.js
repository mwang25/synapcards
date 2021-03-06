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

  // First pop gives cardId, which is userId:num
  var cardId = window.location.pathname.split("/").pop();
  // The next 3 vars are passed into the backend to authenticate the user.
  var userIdToken = null;
  var userId = cardId.split(":")[0];
  var cardNum = cardId.split(":")[1];
  // Signed in user data stored across functions.
  var cardData = null;
  // Params from the query portion of the URL
  var queryParams = {'op': 'default'};

  // Firebase log-in
  function configureFirebaseLogin() {

    firebase.initializeApp(config);

    // [START onAuthStateChanged]
    firebase.auth().onAuthStateChanged(function(user) {
      parseQueryParams(window.location.search.substr(1));
      if (user) {
        user.getToken().then(function(idToken) {
          userIdToken = idToken;
          $('#signed-in-top').show();
          $('#signed-out-top').hide();
          $('#static-card-section').show();
          $('#heart-filled-icon').hide();
          $('#heart-hollow-icon').hide();
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
            // Signed in, but could be viewing another user's card
            cardData = data;
            $('#signed-in-user-id-top').text(data.signed_in_user_id);
            link = backendHostUrl + '/user/' + data.signed_in_user_id;
            $('#self-profile-link-top').attr('href', link);
            console.log("card user_id:" + userId);
            console.log("signed_in_user_id:" + data.signed_in_user_id);
            $('#static-card-section').hide();
            if (userId == data.signed_in_user_id) {
              console.log("matched signed in user (viewing own card)");
              if (cardNum == 0) {
                showForm();
              } else if (queryParams['op'] == 'edit') {
                console.log("edit card");
                fillForm();
                showForm();
              } else {
                console.log("fill dynamic card");
                fillDynamicCard();
                $('#dynamic-card-section').show();
                setLikeState();
                console.log("showing buttons");
                $('#buttons-section').show();
              }
            } else {
              console.log("signed in user (viewing someone else's card)");
              fillDynamicCard();
              $('#dynamic-card-section').show();
              setLikeState();
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

  function parseQueryParams(qstr) {
    console.log("qstr:" + qstr);
    var arr = qstr.split("&");
    for (var i = 0; i < arr.length; i++) {
        console.log("arr: " + arr[i]);
        if (/=/.test(arr[i])) {
            var p = arr[i].split("=");
            var val = decodeURIComponent(p[1].replace(/\+/g, ' '));
            console.log(p[0] + " = " + val);
            queryParams[p[0]] = val;
        }
    }
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
    $('#dynamic-num-likes').text(cardData.num_likes);
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
    $('#dynamic-created').text(cardData.created_loc);
    $('#dynamic-updated').text(cardData.updated_loc);
    $('#dynamic-liked-by').text(cardData.liked_by);
  }

  function setLikeState() {
    console.log("cardData.liked_by " + cardData.liked_by);
    liked_by = cardData.liked_by.split(", ").map(s => s.trim());
    console.log("trimmed_arr " + liked_by);
    console.log("signed_in_user_id " + cardData.signed_in_user_id);
    if (liked_by.indexOf(cardData.signed_in_user_id) > -1) {
      $('#heart-filled-icon').show();
    } else {
      $('#heart-hollow-icon').show();
    }
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
    url = backendHostUrl + '/card/' + userId + ':0';
    console.log("new card op redirect to: " + url);
    window.location.href=url;
  });

  var editBtn =$('#edit-button');
  editBtn.click(function(event) {
    event.preventDefault();
    url = backendHostUrl + '/card/' + cardId + '?op=edit';
    console.log("edit card redirect to: " + url);
    window.location.href=url;
  });

  var cancelBtn =$('#cancel-button');
  cancelBtn.click(function(event) {
    event.preventDefault();
    url = backendHostUrl + '/card/' + cardId;
    console.log("edit canceled, redirect to: " + url);
    window.location.href=url;
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
        console.log("card saved");
        url = backendHostUrl + '/card/' + data.card_id;
        console.log("post save redirect: " + url);
        window.location.href=url;
      }
    });
  });

  function likeOperation(op) {
    console.log("likeOperation op: " + op)
    console.log("likeOperation cardId: " + cardId)
    $.ajax(backendHostUrl + '/likeajax', {
      headers: {
        'Authorization': 'Bearer ' + userIdToken
      },
      method: 'POST',
      data: JSON.stringify({
        'action': op,
        'user_id': cardData.signed_in_user_id,
        'card_id': cardId,
      }),
      contentType : 'application/json'
    }).then(function(data){
      if ('error_message' in data) {
        console.log("like ajax error detected: " + data.error_message)
        window.alert(data.error_message);
      } else {
        console.log("like ajax success");
        cardData = data;
        $('#dynamic-num-likes').text(cardData.num_likes);
        $('#dynamic-liked-by').text(cardData.liked_by);
      }
    });
  }

  var heartHollowIcon = $('#heart-hollow-icon');
  heartHollowIcon.click(function(event) {
    event.preventDefault();
    console.log("heart hollow icon hit --> liked");
    heartFilledIcon.show();
    heartHollowIcon.hide();
    likeOperation('like');
  });

  var heartFilledIcon = $('#heart-filled-icon');
  heartFilledIcon.click(function(event) {
    event.preventDefault();
    console.log("heart filled icon hit --> unliked");
    heartFilledIcon.hide();
    heartHollowIcon.show();
    likeOperation('unlike');
  });

  configureFirebaseLogin();
});
