from os import path
from typing import Literal
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from agents.find_images.state import FindImagesState
from agents.find_images.configuration import FindImagesConfiguration
from agents.utils import get_link_type, load_chat_model
from agents.find_images.utils import *
from agents.utils import is_valid_url
from langchain_core.documents import Document

def mock_find_images_state() -> FindImagesState:
    return FindImagesState(
        relevant_links= ["https://www.cnbc.com/2025/01/30/openai-partners-with-us-national-laboratories-on-scientific-research.html"],
        page_contents= [Document(page_content="nMenu\n\nKey Points\n\n- OpenAI said the U.S. National Laboratories will be using its latest artificial intelligence models for scientific research and nuclear weapons security.\n- The company will work with Microsoft to deploy an OpenAI model on Venado, the supercomputer at Los Alamos National Laboratory.\n- Earlier this week, OpenAI released ChatGPT Gov, an AI platform built specifically for U.S. government use.\n\n![OpenAI CEO Sam Altman speaks next to SoftBank CEO Masayoshi Son after U.S. President Donald Trump delivered remarks on AI infrastructure at the Roosevelt room at White House in Washington, U.S., January 21, 2025.  REUTERS/Carlos Barria](https://image.cnbcfm.com/api/v1/image/108090116-17374997272025-01-21t224807z_2088858685_rc2meca5paf6_rtrmadp_0_usa-trump.jpeg?v=1738271864&w=1858&h=1045&vtcrop=y)\n\nOpenAI CEO Sam Altman speaks next to SoftBank CEO Masayoshi Son after U.S. President Donald Trump delivered remarks on AI infrastructure at the Roosevelt Room in the White House in Washington on Jan. 21, 2025.\n\nCarlos Barria \\| Reuters\n\nOpenAI on Thursday said the U.S. National Laboratories will be using its latest artificial intelligence models for scientific research and nuclear weapons security.\n\nUnder the agreement, up to 15,000 scientists working at the National Laboratories may be able to access OpenAI’s reasoning-focused o1 series. OpenAI will also work with [Microsoft](https://www.cnbc.com/quotes/MSFT/), its lead investor, to deploy one of its models on Venado, the supercomputer at Los Alamos National Laboratory, according to a release. Venado is powered by technology from [Nvidia](https://www.cnbc.com/quotes/NVDA/) and [Hewlett-Packard Enterprise](https://www.cnbc.com/quotes/HPE/).\n\nOpenAI CEO Sam Altman announced the partnership at a company event called “Building to Win: AI Economics,” in Washington, D.C.\n\nAccording to OpenAI, the new partnership will involve scientists using OpenAI’s technology to enhance cybersecurity to protect the U.S. power grid, identify new approaches to treating and preventing diseases and deepen understanding of fundamental mathematics and physics.\n\nIt will also involve work on nuclear weapons, “focused on reducing the risk of nuclear war and securing nuclear materials and weapons worldwide,” the company wrote. Some OpenAI researchers with security clearances will consult on the project.\n\n## Read more CNBC reporting on AI\n\n- [Perplexity AI revises Tiktok merger proposal that could give the U.S. government a 50% stake](https://www.cnbc.com/2025/01/26/perplexity-tiktok-revised-merger-proposal.html)\n- [Trump tariffs could raise prices on technology like laptops, smartphones and AI](https://www.cnbc.com/2025/01/27/trump-tariffs-could-raise-prices-on-laptops-smartphones-and-ai-.html)\n- [OpenAI introduces Operator to automate tasks such as vacation planning, restaurant reservations](https://www.cnbc.com/2025/01/23/openai-operator-ai-agent-can-automate-tasks-like-vacation-planning.html)\n- [Zuckerberg sets Meta’s AI targets for the year, expects to spend $60 billion on growth](https://www.cnbc.com/2025/01/24/zuckerberg-sets-metas-ai-targets-for-the-year-expects-to-spend-60-billion-on-growth.html)\n- [Scale AI CEO says China has quickly caught the U.S. with the DeepSeek open-source model](https://www.cnbc.com/2025/01/23/scale-ai-ceo-says-china-has-quickly-caught-the-us-with-deepseek.html)\n\nEarlier this week, OpenAI released [ChatGPT Gov](https://www.cnbc.com/2025/01/28/openai-launches-chatgpt-gov-for-us-government-agencies.html), an AI platform built specifically for U.S. government use. OpenAI billed the new platform as a step beyond ChatGPT Enterprise as far as security. It will allow government agencies to feed “non-public, sensitive information” into OpenAI’s models while operating within their own secure hosting environments, the company said.\n\nOpenAI said that since the beginning of 2024, more than 90,000 employees of federal, state and local governments have generated over 18 million prompts within ChatGPT, using the technology to translate and summarize documents, write and draft policy memos, generate code and build applications.\n\nThe government partnership follows a series of moves by Altman and OpenAI that appear to be targeted at appeasing [President Donald Trump](https://www.cnbc.com/donald-trump/). Altman [contributed $1 million](https://www.cnbc.com/2025/01/09/google-donates-1-million-to-trumps-inauguration-fund.html) to the inauguration, attended the event last week alongside other tech CEOs and recently signaled his admiration for the president.\n\nAltman wrote on X that watching Trump “more carefully recently has really changed my perspective on him,” adding that “he will be incredible for the country in many ways.” OpenAI is also part of the recently announced [Stargate](https://www.cnbc.com/2025/01/23/from-musk-to-nadella-tech-ceos-spar-over-trumps-stargate-ai-project.html) project that involves billions of dollars in investment into U.S. AI infrastructure.\n\nAs OpenAI steps up its ties to the government, a Chinese rival is blowing up in the U.S. DeepSeek, an AI startup lab out of China, saw its app [soar](https://www.cnbc.com/2025/01/27/chinas-deepseek-ai-tops-chatgpt-app-store-what-you-should-know.html) to the top of [Apple’s](https://www.cnbc.com/quotes/AAPL/) App Store rankings this week and roiled U.S. markets on reports that its powerful model was trained at a fraction of the cost of U.S. competitors.\n\nAltman described DeepSeek’s R1 model as “impressive,” and [wrote on X](https://x.com/sama/status/1884066337103962416) that “we will obviously deliver much better models and also it’s legit invigorating to have a new competitor!”\n\n**WATCH:** [OpenAI highly overvalued](https://www.cnbc.com/video/2025/01/28/openai-is-highly-overvalued-and-deepseek-just-blew-up-their-business-model-says-nyus-gary-marcus.html)\n\n![OpenAI is highly overvalued and DeepSeek just blew up their business model, says NYU's Gary Marcus](https://image.cnbcfm.com/api/v1/image/108093511-17380798311738079829-38192865376-1080pnbcnews.jpg?v=1738079830&w=750&h=422&vtcrop=y)\n\nwatch now\n\nVIDEO4:0004:00\n\nOpenAI is highly overvalued and DeepSeek just blew up their business model, says NYU’s Gary Marcus\n\n[Squawk on the Street](https://www.cnbc.com/squawk-on-the-street/)\n\nRelated\n\n1. [![CEO of writer.com May Habib attends the Harper's Bazaar At Work Summit, in partnership with Porsche and One&Only One Za'abeel, at Raffles London at The OWO on November 21, 2023 in London, England.](https://image.cnbcfm.com/api/v1/image/108045487-1728497238498-108045487-1728493354818-gettyimages-1794149442-ssp_7171.jpeg?v=1728497277&h=150&w=200)](https://www.cnbc.com/2024/10/09/ai-startup-writer-launches-new-model-to-compete-with-openai.html)\n[AI startup Writer launches new model to compete with OpenAI](https://www.cnbc.com/2024/10/09/ai-startup-writer-launches-new-model-to-compete-with-openai.html)\n\n2. [![A sign is posted in front of the Nvidia headquarters in Santa Clara, California, on May 10, 2018.](https://image.cnbcfm.com/api/v1/image/107248164-1685469697358-gettyimages-957037018-100038699.jpeg?v=1704735135&h=150&w=200)](https://www.cnbc.com/2023/10/17/us-bans-export-of-more-ai-chips-including-nvidia-h800-to-china.html)\n[U.S. curbs export of more AI chips, including Nvidia H800, to China](https://www.cnbc.com/2023/10/17/us-bans-export-of-more-ai-chips-including-nvidia-h800-to-china.html)\n\n3. [![Sam Altman, CEO of OpenAI, at the Hope Global Forums annual meeting in Atlanta on Dec. 11, 2023.](https://image.cnbcfm.com/api/v1/image/107346332-1702387207643-gettyimages-1841164541-HOPE_GLOBAL_FORUMS.jpeg?v=1727474008&h=150&w=200)](https://www.cnbc.com/2024/09/27/openai-sees-5-billion-loss-this-year-on-3point7-billion-in-revenue.html)\n[OpenAI sees roughly $5 billion loss this year on $3.7 billion in revenue](https://www.cnbc.com/2024/09/27/openai-sees-5-billion-loss-this-year-on-3point7-billion-in-revenue.html)\n\n4. [![Samsung S25 Ultra on display at one of Samsung's stores in London, U.K. Samsung has boosted the capabilities of the S25 on the Ultra model.](https://image.cnbcfm.com/api/v1/image/108086826-1736946625466-20250115_091902.jpg?v=1736946769&h=150&w=200)](https://www.cnbc.com/2025/01/22/samsung-s25-series-launch-specs-price-release-date-ai-features.html)\n[Samsung launches S25 smartphone with boosted AI as Apple battle heats up](https://www.cnbc.com/2025/01/22/samsung-s25-series-launch-specs-price-release-date-ai-features.html)\n\n\n![Company Logo](https://cdn.cookielaw.org/logos/17e5cb00-ad90-47f5-a58d-77597d9d2c16/ffe22c24-b5ec-419d-a0f9-f090bf07f6f0/9366d06d-524a-4047-b900-ba2d60e62e46/NBCU_logo.png)\n\nResidents of one of the states listed in the ‘Your Rights’ section of NBCUniversal’s Privacy Policy we have received your Global Privacy Control signal or you have opted out from the toggle below, but there is another step. To opt out of us selling or sharing/processing data such as your name, email address and other associated personal information for targeted advertising activities as described above, please submit the form below. ALL OTHER LOCATIONS: If we do not detect that you are in one of the states listed in the ‘Your Rights’ section of NBCUniversal’s Privacy Policy, these choices will not apply even if you toggle this button off.\n\n## Your Privacy Choices: Opt-out of sale of personal information and Opt-out of sharing or processing personal information for targeted ads\n\nTo provide you with a more relevant online experience, certain online ad partners may combine personal information that we make available with data across different businesses and otherwise assist us with related advertising activities, as described in our [Privacy Policy](https://www.nbcuniversal.com/privacy). This may be considered “selling” or “sharing/processing” for targeted online advertising under applicable law.\n\nIf you are a resident of one of the states listed in the [‘Your Rights’](https://www.nbcuniversal.com/privacy#accordionheader5) section of NBCUniversal’s Privacy Policy, to opt out of us selling or sharing/processing your personal information:\n\n- such as cookies and devices identifiers for the targeted ads and related purposes for this site/app on this browser/device: switch the “Allow Sale of My Personal Info or Sharing/Processing for Targeted Ads” toggle under Manage Preferences to OFF (grey color) by moving it LEFT and clicking “Confirm My Choice”.\n- such as your name, email address and other associated personal information for targeted advertising activities as described above, please submit the form below.\n\n**Please note that choices related to cookies and device identifiers are specific to the brand’s website or app on the browser or device where you are making the election.**\n\n### Manage Preferences: Toggle Off and Click ‘Confirm My Choice’ and Complete Opt-Out Form to Opt-Out\n\n#### Allow Sale of My Personal Info and Sharing/Processing for Targeted Ads\n\nAllow Sale of My Personal Info and Sharing/Processing for Targeted Ads\n\n**Resident of the states listed in the ‘Your Rights’ section of NBCUniversal’s Privacy Policy Only:** To opt out of selling or sharing/processing for targeted advertising of information such as cookies and device identifiers processed for targeted ads (as defined by law) and related purposes for this site/app on this browser/device, switch this toggle to off (grey color) by moving it left and clicking **“Confirm My Choice”** below. (This will close this dialogue box, so please open the email Opt-Out Form 1st).")],
        post= "🚨 **AI Meets Nuclear Security** ⚠️  \nOpenAI just partnered with the U.S. National Laboratories to harness AI for scientific research and nuclear weapons security. \n\nIntegrating advanced AI into national security...what could possibly go wrong? 🤔 This collaboration could transform cybersecurity and nuclear safety, but it raises urgent ethical questions. Are we prepared for AI's pivotal role in defense?\n\nWhat do you think about this bold move? Share your thoughts in the comments! \n\nRead more here: [OpenAI Partners with U.S. National Laboratories](https://www.cnbc.com/2025/01/30/openai-partners-with-us-national-laboratories-on-scientific-research.html)\n\n#AIandSecurity #NuclearEthics #OpenAI #FutureOfAI #TechForGood",
    )

async def find_images(
    state: FindImagesState, config: RunnableConfig
) -> FindImagesState:
    """Locate image urls referenced in page_contents and add them to state.image_options."""
    # state = mock_find_images_state()
    image_urls = []
    link = state.relevant_links[0]
    link_type = get_link_type(link)
    match link_type:
        case "general":
            for options in state.image_options:
                image_urls.append(options)
            if state.page_contents:
                for doc in state.page_contents:
                    extracted_urls = (filter_image_urls(extract_image_urls(doc.page_content)))
                    for url in extracted_urls:
                        if is_valid_url(url):
                            if get_link_type(url) != "github":
                                image_urls.append(url)
                            else:
                                # TODO: Implement GitHub link type
                                raise ValueError("GitHub link type not yet implemented.")
                                #   // If a full github URL. extract the file name from the path. to do this, extract the path after `blob/<branch>`
                                #   const filePath = urlOrPathname.match(/blob\/[^/]+\/(.+)/)?.[1];
                                #   if (!filePath) {
                                #     if (!checkIsGitHubImageUrl(urlOrPathname)) {
                                #       console.warn(
                                #         "Could not extract file path from URL",
                                #         urlOrPathname,
                                #       );
                                #     } else {
                                #       imageUrls.add(urlOrPathname);
                                #     }
                                #     continue;
                                #   }
                                #   const getContents = await getFileContents(urlOrPathname, filePath);
                                #   if (getContents.download_url) {
                                #     imageUrls.add(getContents.download_url);
                                #   }
                        else:
                            # assume it's a path relative to link
                            image_urls.append(path.join(link, url))
            else:
                raise ValueError("No page content found.")               
        case "github":
            raise NotImplementedError("GitHub link type not yet implemented.")
        case "linkedin":
            raise NotImplementedError("LinkedIn link type not yet implemented.")
        case "reddit":
            raise NotImplementedError("Reddit link type not yet implemented.")
        case "twitter":
            raise NotImplementedError("Twitter link type not yet implemented.")
        case "youtube":
            raise NotImplementedError("YouTube link type not yet implemented.")
        case _:
            raise ValueError(f"Unknown link type: {link_type}")

    return {
        "post": state.post,
        "relevant_links": state.relevant_links,
        "page_contents": state.page_contents,
        "image_options": image_urls,
    }

async def validate_images(
    state: FindImagesState, *, config: RunnableConfig
) -> FindImagesState:
    """Use AI vision to examine images in state.image_options and validate they are pertinent to the post content."""
    
    config = FindImagesConfiguration.from_runnable_config(config)
    # TODO: examine urls of state.image_options and determine if they are from protected sources like SUPABASE_URL or https://i.ytimg.com/
    unprotected_image_urls = state.image_options

    # Break unprotected_image_urls into arrays of 10 elements each (chunks)
    chunked_image_urls = chunk_array(unprotected_image_urls, 10)
    all_relevant_indices = []
    # this tracks offset between chunks and the unprotected_image_urls array
    base_index = 0
    # process each chunk of image urls
    for chunk in chunked_image_urls:
        image_messages = await get_images_messages(chunk, base_index)
        # no messages? skip
        if not image_messages:
            continue
        
        try:
            # call model to validate images in the chunk
            model = load_chat_model(config.validate_image_model)
            response = await model.ainvoke(
                [
                    SystemMessage(build_validate_images_prompt(state, config)),
                    HumanMessage(image_messages),
                ]
            )
            chunk_analysis = parse_validate_images_response(response.content)
            # translate chunk index values to global index values (their value in the image_options array)
            global_indices = [i + base_index for i in chunk_analysis]
            all_relevant_indices.extend(global_indices)
        except Exception as e:
            # TODO: log error about problem validating chunk
            pass
        # increment offset for next chunk
        base_index += len(chunk)

    # create array by selecting only the relevant image indices from the unprotected_image_urls array
    validated_image_options = [unprotected_image_urls[i] for i in all_relevant_indices]
    return {
        "image_options": validated_image_options,
    }

async def rerank_images(
    state: FindImagesState, config: RunnableConfig
) -> FindImagesState:
    """Use AI Vision to examine the images and rank them by relevancy to the post."""
    # skip if there is only 0 or 1 image options
    if len(state.image_options) < 2:
        return {
            "image_options": state.image_options,
        }
    config = FindImagesConfiguration.from_runnable_config(config)
    # create chunks of 5 image options
    chunked_image_urls = chunk_array(state.image_options, 5)
    reranked_indices = []
    failed_indices = []
    # track offset between chunks and the state.image_options array
    base_index = 0
    # process each chunk of image urls
    for chunk in chunked_image_urls:
        image_messages = await get_images_messages(chunk, base_index)
        if not image_messages:
            continue

        try:
            model = load_chat_model(config.rerank_image_model)
            response = await model.ainvoke(
                [
                    SystemMessage(build_rerank_images_prompt(state, config)),
                    HumanMessage(image_messages),
                ]
            )
            chunk_analysis = parse_rerank_images_response(response.content)
            # translate chunk index values to global index values (their value in the image_options array)
            global_indices = [i + base_index for i in chunk_analysis]
            reranked_indices.extend(global_indices)

        except Exception as e:
            # TODO log error about problem reranking chunk
            failed_indices.extend(range(base_index, base_index + len(chunk)))
            pass
        # increment offset for next chunk
        base_index += len(chunk)

    if len(reranked_indices) != len(state.image_options):
        # TODO log warn about rerank size not matching image options size
        return {
            "image_options": state.image_options,
        }
    ranked_image_options = [state.image_options[i] for i in reranked_indices]

    return {
        "image_options": ranked_image_options,
    }

def route_validate_images(
        state: FindImagesState, config: RunnableConfig
    ) -> Literal["validate_images", "__end__"]:
    """Determine if image validation should be performed."""
    if state.image_options:
        return "validate_images"
    return END
    
# Define the graph
builder = StateGraph(state_schema=FindImagesState, config_schema=FindImagesConfiguration)
builder.add_node(find_images)
builder.add_node(validate_images)
builder.add_node(rerank_images)
builder.add_edge(START, "find_images")
builder.add_conditional_edges("find_images", route_validate_images)
builder.add_edge("validate_images", "rerank_images")
builder.add_edge("rerank_images", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "Find Images Graph"
