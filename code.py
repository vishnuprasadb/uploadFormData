def uploadFormData(request, session_id, auth_token):
        
        logr.info("Incoming request to upload form-media files by user:%s"%(request.user))
        resp = {}

        if request.method != 'POST':
                return _return_json_error("Only POST method supported")

        # Fetch the candidate from the request.user
        try:
                candidate = Candidate.objects.get(user_id = request.user.id)
        except:
                return _return_json_error("Not Authenticated!")

        # Check for valid session
        try:
                appSession = ApplicationSession.objects.get(id = session_id)    
        except Exception:
                return _return_json_error("Candidate Application Session doesn't exist!")

        # Check the session_id belongs to same candidate.
        if appSession.applicant.candidate != candidate:
                return _return_json_error("Invalid Candidate Application Flow!")

        # Check the status of appSession -- allow upload only if the status is open
        if appSession.status != "open":
                return _return_json_error("Candidate Application Flow is closed!")

         # Make a token out of the candidate_id, session_id and token. 
        expected_auth_token = _make_media_token(session_id, candidate.id)

        # Verify with the token and save the file.
        if expected_auth_token == auth_token:
                f = request.FILES['file']
                split_name = f.name.split('.') #To distinguish between the '.' in filename and extension if any, last one will be the extension
                extension = split_name[-1]

                _map_extensions = {
                                   "mp3": "audio",
                                   "wav": "audio",
                                   "mp4": "video",
                                   "webm": "video",
                                   "png": 'photo',
                                   "jpg": 'photo',
                                   "jpeg": 'photo',
                                }

                # Fetch the candidate profile to save the filenames.    
                profile = Profile.objects.get(candidate_id = candidate.id)

                # Build the filename based on the extension
                if _map_extensions[extension] == 'photo':
                        filename = 'candidate_%d.%s'%(candidate.id, extension)
                        profile.photo_filename = filename
                if _map_extensions[extension] == 'audio':
                        filename = 'audio_resume_%d.%s'%(candidate.id, extension)
                        profile.audio_profile = filename
                elif _map_extensions[extension] == 'video':
                        filename = 'video_resume_%d.%s'%(candidate.id, extension)
                        profile.video_profile = filename

                path = '/content/candidates/resume/%s'%filename
                o_file = open(path, 'w')

                for chunk in f.chunks():
                        o_file.write(chunk)
                o_file.close()
                profile.save()

                resp["status"] = "success"
                resp["path"] = path.replace('/content', './images/content/s3content')

        else:
                resp["status"] = "failed"
                resp["errStr"] = "Auth Token Mismatch"

        return JsonResponse(resp)
# End of UploadFormData()
