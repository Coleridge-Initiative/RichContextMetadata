#!/usr/bin/env python
# coding: utf-8

# In[3]:


import gen_datasets


# In[ ]:


if pub_url:
           pub_id = "publication-{}".format(get_hash([doi, journal, title]))
           yield doi, pub_id, pub_url, journal, title


# In[4]:


title = 'Cyclical Investment Behavior across Financial Institutions'
doi = '10.1016/j.jfineco.2018.04.012'
journal = 'Journal of Financial Economics'


# In[5]:


gen_datasets.get_hash([doi, journal, title])


# In[ ]:




