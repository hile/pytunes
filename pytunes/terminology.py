"""
iTunes appscript terminology from osascript
"""

version = 1.1
path = '/Applications/iTunes.app'

classes = [
    ('print_settings', 'pset'),
    ('AirPlay_device', 'cAPD'),
    ('application', 'capp'),
    ('double_integer', 'comp'),
    ('picture', 'PICT'),
    ('artwork', 'cArt'),
    ('audio_CD_playlist', 'cCDP'),
    ('audio_CD_track', 'cCDT'),
    ('browser_window', 'cBrW'),
    ('encoder', 'cEnc'),
    ('EQ_preset', 'cEQP'),
    ('EQ_window', 'cEQW'),
    ('file_track', 'cFlT'),
    ('folder_playlist', 'cFoP'),
    ('item', 'cobj'),
    ('library_playlist', 'cLiP'),
    ('miniplayer_window', 'cMPW'),
    ('playlist', 'cPly'),
    ('playlist_window', 'cPlW'),
    ('radio_tuner_playlist', 'cRTP'),
    ('shared_track', 'cShT'),
    ('source', 'cSrc'),
    ('subscription_playlist', 'cSuP'),
    ('track', 'cTrk'),
    ('URL_track', 'cURT'),
    ('user_playlist', 'cUsP'),
    ('video_window', 'cNPW'),
    ('visual', 'cVis'),
    ('window', 'cwin')
]

enums = [
    ('track_listing', 'kTrk'),
    ('album_listing', 'kAlb'),
    ('cd_insert', 'kCDi'),
    ('standard', 'lwst'),
    ('detailed', 'lwdt'),
    ('stopped', 'kPSS'),
    ('playing', 'kPSP'),
    ('paused', 'kPSp'),
    ('fast_forwarding', 'kPSF'),
    ('rewinding', 'kPSR'),
    ('off', 'kRpO'),
    ('one', 'kRp1'),
    ('all', 'kAll'),
    ('songs', 'kShS'),
    ('albums', 'kShA'),
    ('groupings', 'kShG'),
    ('small', 'kVSS'),
    ('medium', 'kVSM'),
    ('large', 'kVSL'),
    ('library', 'kLib'),
    ('iPod', 'kPod'),
    ('audio_CD', 'kACD'),
    ('MP3_CD', 'kMCD'),
    ('radio_tuner', 'kTun'),
    ('shared_library', 'kShd'),
    ('iTunes_Store', 'kITS'),
    ('unknown', 'kUnk'),
    ('albums', 'kSrL'), ('artists', 'kSrR'),
    ('composers', 'kSrC'),
    ('displayed', 'kSrV'),
    ('songs', 'kSrS'),
    ('none', 'kNon'),
    ('Books', 'kSpA'),
    ('folder', 'kSpF'),
    ('Genius', 'kSpG'),
    ('iTunes_U', 'kSpU'),
    ('Library', 'kSpL'),
    ('Movies', 'kSpI'),
    ('Music', 'kSpZ'),
    ('Podcasts', 'kSpP'),
    ('Purchased_Music', 'kSpM'),
    ('TV_Shows', 'kSpT'),
    ('alert_tone', 'kMdL'),
    ('audiobook', 'kMdA'),
    ('book', 'kMdB'),
    ('home_video', 'kVdH'),
    ('iTunesU', 'kMdI'),
    ('movie', 'kVdM'),
    ('song', 'kMdS'),
    ('music_video', 'kVdV'),
    ('podcast', 'kMdP'),
    ('ringtone', 'kMdR'),
    ('TV_show', 'kVdT'),
    ('voice_memo', 'kMdO'),
    ('user', 'kRtU'),
    ('computed', 'kRtC'),
    ('computer', 'kAPC'),
    ('AirPort_Express', 'kAPX'),
    ('Apple_TV', 'kAPT'),
    ('AirPlay_device', 'kAPO'),
    ('unknown', 'kAPU'),
    ('purchased', 'kPur'),
    ('matched', 'kMat'),
    ('uploaded', 'kUpl'),
    ('ineligible', 'kRej'),
    ('removed', 'kRem'),
    ('error', 'kErr'),
    ('duplicate', 'kDup'),
    ('subscription', 'kSub'),
    ('no_longer_available', 'kRev'),
    ('not_uploaded', 'kUpP')
]

properties = [
    ('active', 'pAct'),
    ('address', 'pURL'),
    ('AirPlay_enabled', 'pAPE'),
    ('album', 'pAlb'),
    ('album_artist', 'pAlA'),
    ('album_disliked', 'pAHt'),
    ('album_loved', 'pALv'),
    ('album_rating', 'pAlR'),
    ('album_rating_kind', 'pARk'),
    ('artist', 'pArt'),
    ('available', 'pAva'),
    ('band_1', 'pEQ1'),
    ('band_10', 'pEQ0'),
    ('band_2', 'pEQ2'),
    ('band_3', 'pEQ3'),
    ('band_4', 'pEQ4'),
    ('band_5', 'pEQ5'),
    ('band_6', 'pEQ6'),
    ('band_7', 'pEQ7'),
    ('band_8', 'pEQ8'),
    ('band_9', 'pEQ9'),
    ('bit_rate', 'pBRt'),
    ('bookmark', 'pBkt'),
    ('bookmarkable', 'pBkm'),
    ('bounds', 'pbnd'),
    ('bpm', 'pBPM'),
    ('capacity', 'capa'),
    ('category', 'pCat'),
    ('class_', 'pcls'),
    ('closeable', 'hclb'),
    ('cloud_status', 'pClS'),
    ('collapseable', 'pWSh'),
    ('collapsed', 'wshd'),
    ('collating', 'lwcl'),
    ('comment', 'pCmt'),
    ('compilation', 'pAnt'),
    ('composer', 'pCmp'),
    ('container', 'ctnr'),
    ('converting', 'pCnv'),
    ('copies', 'lwcp'),
    ('current_AirPlay_devices', 'pAPD'),
    ('current_encoder', 'pEnc'),
    ('current_EQ_preset', 'pEQP'),
    ('current_playlist', 'pPla'),
    ('current_stream_title', 'pStT'),
    ('current_stream_URL', 'pStU'),
    ('current_track', 'pTrk'),
    ('current_visual', 'pVis'),
    ('data', 'pPCT'),
    ('database_ID', 'pDID'),
    ('date_added', 'pAdd'),
    ('description', 'pDes'),
    ('disc_count', 'pDsC'),
    ('disc_number', 'pDsN'),
    ('disliked', 'pHat'),
    ('downloaded', 'pDlA'),
    ('downloader_Apple_ID', 'pDAI'),
    ('downloader_name', 'pDNm'),
    ('duration', 'pDur'),
    ('enabled', 'enbl'),
    ('ending_page', 'lwlp'),
    ('episode_ID', 'pEpD'),
    ('episode_number', 'pEpN'),
    ('EQ', 'pEQp'),
    ('EQ_enabled', 'pEQ '),
    ('error_handling', 'lweh'),
    ('fax_number', 'faxn'),
    ('finish', 'pStp'),
    ('fixed_indexing', 'pFix'),
    ('format', 'pFmt'),
    ('free_space', 'frsp'),
    ('frontmost', 'pisf'),
    ('full_screen', 'pFSc'),
    ('gapless', 'pGpl'),
    ('genius', 'pGns'),
    ('genre', 'pGen'),
    ('grouping', 'pGrp'),
    ('id', 'ID  '),
    ('index', 'pidx'),
    ('kind', 'pKnd'),
    ('location', 'pLoc'),
    ('long_description', 'pLds'),
    ('loved', 'pLov'),
    ('lyrics', 'pLyr'),
    ('media_kind', 'pMdK'),
    ('modifiable', 'pMod'),
    ('modification_date', 'asmo'),
    ('movement', 'pMNm'),
    ('movement_count', 'pMvC'),
    ('movement_number', 'pMvN'),
    ('mute', 'pMut'),
    ('name', 'pnam'),
    ('network_address', 'pMAC'),
    ('pages_across', 'lwla'),
    ('pages_down', 'lwld'),
    ('parent', 'pPlP'),
    ('persistent_ID', 'pPIS'),
    ('played_count', 'pPlC'),
    ('played_date', 'pPlD'),
    ('player_position', 'pPos'),
    ('player_state', 'pPlS'),
    ('position', 'ppos'),
    ('preamp', 'pEQA'),
    ('printer_features', 'lwpf'),
    ('properties', 'pALL'),
    ('protected', 'pPro'),
    ('purchaser_Apple_ID', 'pPAI'),
    ('purchaser_name', 'pPNm'),
    ('rating', 'pRte'),
    ('rating_kind', 'pRtk'),
    ('raw_data', 'pRaw'),
    ('release_date', 'pRlD'),
    ('requested_print_time', 'lwqt'),
    ('resizable', 'prsz'),
    ('sample_rate', 'pSRt'),
    ('season_number', 'pSeN'),
    ('selected', 'selc'),
    ('selection', 'sele'),
    ('shared', 'pShr'),
    ('show', 'pShw'),
    ('shufflable', 'pSfa'),
    ('shuffle', 'pShf'),
    ('shuffle_enabled', 'pShE'),
    ('shuffle_mode', 'pShM'),
    ('size', 'pSiz'),
    ('skipped_count', 'pSkC'),
    ('skipped_date', 'pSkD'),
    ('smart', 'pSmt'),
    ('song_repeat', 'pRpt'),
    ('sort_album', 'pSAl'),
    ('sort_album_artist', 'pSAA'),
    ('sort_artist', 'pSAr'),
    ('sort_composer', 'pSCm'),
    ('sort_name', 'pSNm'),
    ('sort_show', 'pSSN'),
    ('sound_volume', 'pVol'),
    ('special_kind', 'pSpK'),
    ('start', 'pStr'),
    ('starting_page', 'lwfp'),
    ('supports_audio', 'pAud'),
    ('supports_video', 'pVid'),
    ('target_printer', 'trpr'),
    ('time', 'pTim'),
    ('track_count', 'pTrC'),
    ('track_number', 'pTrN'),
    ('unplayed', 'pUnp'),
    ('update_tracks', 'pUTC'),
    ('version', 'vers'),
    ('video_kind', 'pVdK'),
    ('view', 'pPly'),
    ('visible', 'pvis'),
    ('visual_size', 'pVSz'),
    ('visuals_enabled', 'pVsE'),
    ('volume_adjustment', 'pAdj'),
    ('work', 'pWrk'),
    ('year', 'pYr '),
    ('zoomable', 'iszm'),
    ('zoomed', 'pzum'),
]

elements = [
    ('AirPlay_devices', 'cAPD'),
    ('applications', 'capp'),
    ('artworks', 'cArt'),
    ('audio_CD_playlists', 'cCDP'),
    ('audio_CD_tracks', 'cCDT'),
    ('browser_windows', 'cBrW'),
    ('encoders', 'cEnc'),
    ('EQ_presets', 'cEQP'),
    ('EQ_windows', 'cEQW'),
    ('file_tracks', 'cFlT'),
    ('folder_playlists', 'cFoP'),
    ('items', 'cobj'),
    ('library_playlists', 'cLiP'),
    ('miniplayer_windows', 'cMPW'),
    ('playlists', 'cPly'),
    ('playlist_windows', 'cPlW'),
    ('radio_tuner_playlists', 'cRTP'),
    ('shared_tracks', 'cShT'),
    ('sources', 'cSrc'),
    ('subscription_playlists', 'cSuP'),
    ('tracks', 'cTrk'),
    ('URL_tracks', 'cURT'),
    ('user_playlists', 'cUsP'),
    ('video_windows', 'cNPW'),
    ('visuals', 'cVis'),
    ('windows', 'cwin')
]

commands = [
    ('exists', 'coredoex', []),
    ('move', 'coremove', [('to', 'insh')]),
    ('subscribe', 'hookpSub', []),
    ('playpause', 'hookPlPs', []),
    ('download', 'hookDwnl', []),
    ('close', 'coreclos', []),
    ('open', 'aevtodoc', []),
    ('select', 'miscslct', []),
    ('open_location', 'GURLGURL', []),
    ('quit', 'aevtquit', []),
    ('pause', 'hookPaus', []),
    ('make', 'corecrel', [
        ('new', 'kocl'),
        ('at', 'insh'),
        ('with_properties', 'prdt')
    ]),
    ('duplicate', 'coreclon', [('to', 'insh')]),
    ('print_', 'aevtpdoc', [
        ('print_dialog', 'pdlg'),
        ('with_properties', 'prdt'),
        ('kind', 'pKnd'),
        ('theme', 'pThm')
    ]),
    ('add', 'hookAdd ', [('to', 'insh')]),
    ('rewind', 'hookRwnd', []),
    ('save', 'coresave', []),
    ('play', 'hookPlay', [('once', 'POne')]),
    ('run', 'aevtoapp', []),
    ('resume', 'hookResu', []),
    ('updatePodcast', 'hookUpd1', []),
    ('next_track', 'hookNext', []),
    ('stop', 'hookStop', []),
    ('search', 'hookSrch', [
        ('for_', 'pTrm'),
        ('only', 'pAre')
    ]),
    ('updateAllPodcasts', 'hookUpdp', []),
    ('update', 'hookUpdt', []),
    ('previous_track', 'hookPrev', []),
    ('fast_forward', 'hookFast', []),
    ('count', 'corecnte', [('each', 'kocl')]),
    ('reveal', 'hookRevl', []),
    ('convert', 'hookConv', []),
    ('eject', 'hookEjct', []),
    ('back_track', 'hookBack', []),
    ('refresh', 'hookRfrs', []),
    ('delete', 'coredelo', [])
]
