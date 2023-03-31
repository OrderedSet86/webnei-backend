



async def get_stickynotes(info):
    """ Get all stickynotes resolver """
    selected_fields = get_only_selected_fields(stickynotes_model.StickyNotes,info)
    async with get_session() as s:
        sql = select(stickynotes_model.StickyNotes).options(load_only(*selected_fields)) \
        .order_by(stickynotes_model.StickyNotes.id)
        db_stickynotes = (await s.execute(sql)).scalars().unique().all()

    stickynotes_data_list = []
    for sticky_note in db_stickynotes:
        sticky_note_dict = get_valid_data(sticky_note,stickynotes_model.StickyNotes)
        stickynotes_data_list.append(StickyNotes(**sticky_note_dict))

    return stickynotes_data_list