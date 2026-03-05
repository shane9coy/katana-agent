## GET USER ID:
curl "https://api.x.com/2/users/by/username/quant_pulse" -H "Authorization: Bearer AAAAAAAAAAAAAAAAAAAAADaP7gEAAAAAV%2FS67Lnt00Iw9lpji8YwyjQg4yU%3DqUEd7igbh6gpFhWESktk8johpv16JmN41EhpNKSXxcMqypUd27"

## Send Single DM
## Create DM by Participant:

curl --request POST \
  --url https://api.x.com/2/dm_conversations/with/{participant_id}/messages \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "text": "<string>",
  "attachments": [
    {
      "media_id": "1146654567674912769"
    }
  ]
}
'

## Send Group DM:
curl --request POST
--url https://api.x.com/2/dm_conversations
--header 'Authorization: Bearer ' \ #token=$(X_SWRLD_BEARER_TOKEN) --header 'Content-Type: application/json'
--data ' { "conversation_type": "Group", "message": { "text": "", "attachments": [ { "media_id": "1146654567674912769" } ] }, "participant_ids": [ "2244994945" ] } '