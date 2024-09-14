





repository = Repository.lookup("benh/resemble-hello")

update_response = await repository.Update(context, body="{... }")




watch_response = await repository.Watch(context, event_type=PR)



####################

var = Var.lookup(watch_response.var_id)

status_response = await var.Status(context)

if status_response.ready

####################

var = Var.lookup(watch_response.var_id)

status_response = await var.Get(context)

if status_response.ready:
    json.loads(status.value)

####################

# in workflow:

var = Var.lookup(watch_response.var_id)

async def var_is_ready():
    status_response = await var.Status(context)
    return status_response.ready


await until(context, var_is_ready)

get_response = await var.Get(context)

####################

# in workflow:

var = Var.lookup(watch_response.var_id)

get_response = await (await var.schedule().Get(context))

####################

# in workflow:

response = await repository.idempotently().Subscribe(context)

events = Stream(Event).lookup(response.stream_id)

async def stream_has_event():
    return (await events.Size(context)).size > 0

await until(context, stream_has_event)

event = await events.Get(context)

channel = slack.Channel.lookup(...)

await channel.idempotently().Post(context, ...)

return Loop()

####################

events = Stream(Event).lookup(response.stream_id)

async def post_to_slack(event: Event):
    channel = slack.Channel.lookup(...)
    await channel.idempotently(f"posting {event.token}").Post(context, ...)

await for_each("GitHub event", context, events, post_to_slack)

####################

await events.Get(context, )


####################

async def get(
    context: WorkflowContext,
):
    async def value():
        while True:
            response = await queue.unidempotently().GetFor(
                context,
                for_id=context.workflow_id,
            )
            if response.HasField("value"):
                return response.value

            status = await queue.Status(context)
            if not status.empty:
                continue

            return False

    return self._deserialize(await until(context, value))


async def pop(
    context: WorkflowContext,
):
    response = await queue.unidempotently().PopFor(
        context,
        for_id=context.workflow_id,
    )


async def foreach(
    context: WorkflowContext,
    f: Callable[[ItemT], Awaitable[None]],
):
    while True:
        item = await self.get(context)

        await f(item)

        await self.pop(context)



async def GetFor(
    self,
    context: TransactionContext,
    state: Queue.State,
    request: GetForRequest,
):
    key = state.gotten_key_for_id.get(request.for_id, None)

    if key is not None:
        entries = await SortedMap.lookup(state.items_id).Range(
            context,
            start_key=key,
            limit=1,
        )
        return GetForResponse(value=entries[0].value)
    elif state.first_available_key != "":
        entries = await SortedMap.lookup(state.items_id).Range(
            context,
            start_key=state.first_available_key,
            limit=2,
        )
        state.gotten_key_for_id[request.for_id] = entries[0].key
        state.first_available_key = entries[1].key if len(entries) > 1 else ""
        return GetForResponse(value=entries[0].value)
    else:
        return GetForResponse()


async def PopFor(
    self,
    context: TransactionContext,
    state: Queue.State,
    request: PopForRequest,
):
    key = state.gotten_key_for_id.pop(request.for_id, None)

    assert key is not None

    await SortedMap.lookup(state.items_id).Remove(context, keys=[key])

    return PopForResponse()


async def Push(
    self,
    context: TransactionContext,
    state: Queue.State,
    request: PushRequest,
):
    key = str(uuid7())

    await SortedMap.lookup(state.items_id).Insert(
        context,
        entries={ key: request.value },
    )

    if state.first_available_key == "":
        state.first_available_key = key

    return PopForResponse()


async def Status(
    self,
    context: ReaderContext,
    state: Queue.State,
    request: StatusRequest,
):
    return StatusResponse(empty=state.first_available_key != "")
